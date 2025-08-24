from typing import Dict, Any
from langgraph.graph import END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ..models.schemas import (
    ResearchPlan, SourceSummary, FinalBrief, UserContext, 
    ResearchStep, SourceType, Reference
)
from ..core.state import ResearchState
from ..core.llms import planning_llm, research_llm
from ..core.tools import search_tools, content_fetcher
from ..utils.logger import logger
from ..models.storage import UserHistoryManager
from datetime import datetime
import asyncio

class ResearchNodes:
    """All nodes for the research workflow with follow-up handling"""

    @staticmethod
    async def summarize_context(state: ResearchState) -> Dict[str, Any]:
        """Summarize user context for follow-up queries"""
        if not state.follow_up:
            return {"user_context": None}
        
        try:
            history_manager = UserHistoryManager()
            user_history = await history_manager.get_user_history(state.user_id)
            
            if not user_history:
                return {"user_context": None}
            
            prompt = ChatPromptTemplate.from_template("""
            Summarize the user's previous research interactions for context.
            
            User ID: {user_id}
            Previous briefs: {history}
            Current topic: {topic}
            
            Focus on:
            1. Previous research topics and findings
            2. User interests and recurring patterns
            3. Relevance to the current topic
            
            Return only the concise summary text.
            """)
            
            chain = prompt | planning_llm
            summary_text = await chain.ainvoke({
                "user_id": state.user_id,
                "history": str(user_history),
                "topic": state.topic
            })
            
            user_context = UserContext(
                user_id=state.user_id,
                previous_briefs=user_history,
                research_interests=[],  # Can optionally infer from history
                last_interaction=user_history[-1]["generated_at"] if user_history else None
            )
            user_context.metadata = {"summary_text": summary_text}
            
            return {"user_context": user_context}
        
        except Exception as e:
            logger.error(f"Context summarization error: {e}")
            state.errors.append(f"Context error: {e}")
            return {"user_context": None}

    @staticmethod
    async def create_research_plan(state: ResearchState) -> Dict[str, Any]:
        """Create a research plan considering user context"""
        try:
            # If follow-up and context available, include it in step descriptions
            if state.follow_up and state.user_context:
                steps = [
                    ResearchStep(
                        step_id="1",
                        description=f"Review previous findings: {state.user_context.metadata.get('summary_text', '')}",
                        priority=1,
                        source_types=[SourceType.WEB, SourceType.ACADEMIC],
                        expected_output="Integrate prior knowledge into updated brief"
                    ),
                    ResearchStep(
                        step_id="2",
                        description=f"Explore new developments related to {state.topic}",
                        priority=2,
                        source_types=[SourceType.NEWS, SourceType.ACADEMIC],
                        expected_output="Identify new findings beyond previous briefs"
                    )
                ]
                plan = ResearchPlan(
                    plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    topic=state.topic,
                    steps=steps
                )
                return {"research_plan": plan}
            
            # Default fallback plan
            return await ResearchNodes.create_fallback_plan(state)
        
        except Exception as e:
            logger.error(f"Research plan creation error: {e}")
            state.errors.append(f"Plan creation error: {e}")
            return await ResearchNodes.create_fallback_plan(state)

    @staticmethod
    async def create_fallback_plan(state: ResearchState) -> Dict[str, Any]:
        """Create a simple 2-step fallback research plan"""
        try:
            steps = [
                ResearchStep(
                    step_id="1",
                    description=f"Research current applications of {state.topic}",
                    priority=1,
                    source_types=[SourceType.WEB, SourceType.NEWS],
                    expected_output="List current applications and use cases"
                ),
                ResearchStep(
                    step_id="2",
                    description=f"Find recent developments in {state.topic}",
                    priority=2,
                    source_types=[SourceType.NEWS, SourceType.ACADEMIC],
                    expected_output="Recent advancements and breakthroughs"
                )
            ]
            plan = ResearchPlan(
                plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                topic=state.topic,
                steps=steps
            )
            return {"research_plan": plan}
        
        except Exception as e:
            logger.error(f"Fallback plan error: {e}")
            state.errors.append(f"Fallback plan error: {e}")
            return {"research_plan": None}

    @staticmethod
    async def execute_search(state: ResearchState) -> Dict[str, Any]:
        """Execute search based on research plan steps"""
        try:
            results = []
            for step in state.research_plan.steps:
                query = f"{state.topic} {step.description}"
                try:
                    search_result = await search_tools.async_search(query)
                    limited = search_result[:2]  # Limit per step
                    for r in limited:
                        r["step_id"] = step.step_id
                        r["priority"] = step.priority
                        r["source_type"] = step.source_types[0] if step.source_types else "web"
                    results.extend(limited)
                except Exception as e:
                    logger.warning(f"Search failed for step {step.step_id}: {e}")
            return {"search_results": results}
        except Exception as e:
            logger.error(f"Search execution error: {e}")
            state.errors.append(f"Search error: {e}")
            return {"search_results": []}

    @staticmethod
    async def fetch_and_summarize_sources(state: ResearchState) -> Dict[str, Any]:
        """Fetch content and create source summaries with fallbacks"""
        summaries = []
        try:
            for result in state.search_results[:2]:
                url = result.get("url", "")
                title = result.get("title", "Unknown")
                snippet = result.get("snippet", "")
                
                content = await content_fetcher.fetch_with_fallback(url, snippet)
                
                try:
                    parser = PydanticOutputParser(pydantic_object=SourceSummary)
                    prompt = ChatPromptTemplate.from_template("""
                    Create a research summary:
                    URL: {url}
                    Title: {title}
                    Content: {content}
                    Topic: {topic}
                    {format_instructions}
                    """)
                    chain = prompt | research_llm | parser
                    summary = await chain.ainvoke({
                        "url": url,
                        "title": title,
                        "content": content[:2000],
                        "topic": state.topic,
                        "format_instructions": parser.get_format_instructions()
                    })
                    summaries.append(summary)
                
                except Exception as e:
                    logger.warning(f"Summarization failed for {url}: {e}")
                    summaries.append(SourceSummary(
                        url=url,
                        title=title,
                        source_type=result.get("source_type", "web"),
                        summary=f"Fallback summary: {snippet[:300]}",
                        key_points=[snippet[:150]] if snippet else ["Info unavailable"],
                        relevance_score=0.6,
                        credibility_score=0.5
                    ))
            return {"source_summaries": summaries}
        
        except Exception as e:
            logger.error(f"Source summarization error: {e}")
            state.errors.append(f"Source summarization error: {e}")
            return {"source_summaries": []}

    @staticmethod
    async def synthesize_brief(state: ResearchState) -> Dict[str, Any]:
        """Generate the final research brief considering user context"""
        try:
            if not state.source_summaries:
                return await ResearchNodes.create_fallback_brief(state)
            
            parser = PydanticOutputParser(pydantic_object=FinalBrief)
            prompt = ChatPromptTemplate.from_template("""
            Create a research brief:
            Topic: {topic}
            Depth: {depth}
            Source Summaries: {summaries}
            User Context: {context}
            {format_instructions}
            """)
            chain = prompt | research_llm | parser
            brief = await chain.ainvoke({
                "topic": state.topic,
                "depth": state.depth,
                "summaries": [s.model_dump() for s in state.source_summaries],
                "context": state.user_context.model_dump() if state.user_context else {},
                "format_instructions": parser.get_format_instructions()
            })
            
            if state.follow_up and state.user_id:
                try:
                    manager = UserHistoryManager()
                    await manager.save_brief(state.user_id, brief)
                except Exception as e:
                    logger.error(f"Saving brief failed: {e}")
            
            return {"final_brief": brief}
        
        except Exception as e:
            logger.error(f"Brief synthesis error: {e}")
            state.errors.append(f"Brief synthesis error: {e}")
            return await ResearchNodes.create_fallback_brief(state)

    @staticmethod
    async def create_fallback_brief(state: ResearchState) -> Dict[str, Any]:
        """Fallback brief when synthesis fails"""
        references = []
        for i, r in enumerate(state.search_results[:2]):
            references.append(Reference(
                url=r.get("url", f"https://example.com/ref-{i}"),
                title=r.get("title", f"Reference {i+1}"),
                citation=f"Online source related to {state.topic}",
                accessed_date=datetime.now()
            ))
        brief = FinalBrief(
            brief_id=f"brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=state.topic,
            executive_summary=f"Overview of {state.topic}.",
            key_findings=[f"{state.topic} key findings."],
            detailed_analysis=f"Analysis of {state.topic} based on available sources.",
            recommendations=[f"Further research in {state.topic}."],
            references=references,
            metadata={"fallback": True, "source_count": len(state.source_summaries)}
        )
        return {"final_brief": brief}

    @staticmethod
    async def handle_errors(state: ResearchState) -> Dict[str, Any]:
        """Log errors if any"""
        if state.errors:
            logger.error(f"Workflow completed with errors: {state.errors}")
        return {"current_step": "completed"}


# Export node functions
nodes = ResearchNodes()