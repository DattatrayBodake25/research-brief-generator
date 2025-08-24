from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
from ..models.schemas import ResearchPlan, SourceSummary, FinalBrief, UserContext

class ResearchState(BaseModel):
    """State for the research workflow"""
    topic: str = Field(..., description="Research topic")
    depth: int = Field(3, description="Research depth")
    user_id: str = Field(..., description="User identifier")
    follow_up: bool = Field(False, description="Follow-up flag")
    
    # Intermediate states
    user_context: Optional[UserContext] = Field(None, description="User context summary")
    research_plan: Optional[ResearchPlan] = Field(None, description="Research plan")
    search_results: List[Dict[str, Any]] = Field(default_factory=list, description="Raw search results")
    source_summaries: List[SourceSummary] = Field(default_factory=list, description="Source summaries")
    final_brief: Optional[FinalBrief] = Field(None, description="Final research brief")
    
    # Execution metadata
    current_step: str = Field("start", description="Current workflow step")
    errors: List[str] = Field(default_factory=list, description="Execution errors")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = Field(None, description="Completion time")

    class Config:
        arbitrary_types_allowed = True