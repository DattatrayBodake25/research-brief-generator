from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal
from .state import ResearchState
from .nodes import nodes
from ..utils.logger import logger

class ResearchWorkflow:
    """LangGraph workflow for research brief generation with follow-up handling"""

    def __init__(self):
        self.graph = StateGraph(ResearchState)
        self._build_graph()

    def _build_graph(self):
        """Build the research workflow graph with conditional branching"""
        
        # Add all nodes
        self.graph.add_node("summarize_context", nodes.summarize_context)
        self.graph.add_node("create_plan", nodes.create_research_plan)
        self.graph.add_node("execute_search", nodes.execute_search)
        self.graph.add_node("summarize_sources", nodes.fetch_and_summarize_sources)
        self.graph.add_node("synthesize_brief", nodes.synthesize_brief)
        self.graph.add_node("handle_errors", nodes.handle_errors)

        # Entry point
        self.graph.set_entry_point("summarize_context")

        # Conditional: decide whether to create plan based on context
        self.graph.add_conditional_edges(
            "summarize_context",
            self._should_create_plan,
            {
                "continue": "create_plan",
                "skip": "execute_search"
            }
        )

        # Main workflow
        self.graph.add_edge("create_plan", "execute_search")
        self.graph.add_edge("execute_search", "summarize_sources")
        self.graph.add_edge("summarize_sources", "synthesize_brief")

        # Conditional: check for errors after synthesis
        self.graph.add_conditional_edges(
            "synthesize_brief",
            self._check_errors,
            {
                "success": END,
                "error": "handle_errors"
            }
        )

        # Error handling node
        self.graph.add_edge("handle_errors", END)

        # Add error checks for intermediate nodes
        for node in ["create_plan", "execute_search", "summarize_sources"]:
            self.graph.add_conditional_edges(
                node,
                self._check_errors,
                {
                    "success": self._next_node(node),
                    "error": "handle_errors"
                }
            )

    def _should_create_plan(self, state: ResearchState) -> Literal["continue", "skip"]:
        """
        Decide if research plan should be created.
        Skip if plan already exists and not a follow-up query.
        """
        if state.research_plan and not state.follow_up:
            return "skip"
        return "continue"

    def _check_errors(self, state: ResearchState) -> Literal["success", "error"]:
        """Check if there are any errors in the workflow state"""
        return "error" if state.errors else "success"

    def _next_node(self, node_name: str) -> str:
        """Determine next node in the workflow if no errors"""
        flow = {
            "create_plan": "execute_search",
            "execute_search": "summarize_sources",
            "summarize_sources": "synthesize_brief"
        }
        return flow.get(node_name, END)

    def compile(self):
        """Compile the workflow graph"""
        return self.graph.compile()


# Create and compile workflow
workflow = ResearchWorkflow()
research_graph = workflow.compile()