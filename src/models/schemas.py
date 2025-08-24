from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ResearchDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"

class SourceType(str, Enum):
    WEB = "web"
    ACADEMIC = "academic"
    NEWS = "news"

class ResearchStep(BaseModel):
    step_id: str = Field(..., description="Unique identifier for the research step")
    description: str = Field(..., description="Description of what to research")
    priority: int = Field(1, ge=1, le=3, description="Priority level (1-3)")
    source_types: List[SourceType] = Field(..., description="Types of sources to search")
    expected_output: str = Field(..., description="Expected format of findings")

class ResearchPlan(BaseModel):
    plan_id: str = Field(..., description="Unique identifier for the research plan")
    topic: str = Field(..., description="Research topic")
    steps: List[ResearchStep] = Field(..., description="Ordered research steps")
    created_at: datetime = Field(default_factory=datetime.now)

class SourceSummary(BaseModel):
    url: HttpUrl = Field(..., description="Source URL")
    title: str = Field(..., description="Source title")
    source_type: SourceType = Field(..., description="Type of source")
    summary: str = Field(..., description="Concise summary of the source")
    key_points: List[str] = Field(..., description="Key points extracted")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance to topic (0-1)")
    credibility_score: float = Field(..., ge=0, le=1, description="Credibility assessment (0-1)")

class Reference(BaseModel):
    url: HttpUrl = Field(..., description="Reference URL")
    title: str = Field(..., description="Reference title")
    citation: str = Field(..., description="Formatted citation")
    accessed_date: datetime = Field(default_factory=datetime.now)

class FinalBrief(BaseModel):
    brief_id: str = Field(..., description="Unique brief identifier")
    topic: str = Field(..., description="Research topic")
    executive_summary: str = Field(..., description="High-level summary")
    key_findings: List[str] = Field(..., description="Main findings")
    detailed_analysis: str = Field(..., description="Comprehensive analysis")
    recommendations: Optional[List[str]] = Field(None, description="Actionable recommendations")
    references: List[Reference] = Field(..., description="Source references")
    generated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class UserContext(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    previous_briefs: List[Dict[str, Any]] = Field(default_factory=list, description="Previous brief summaries")
    research_interests: List[str] = Field(default_factory=list, description="User research interests")
    last_interaction: Optional[datetime] = Field(None, description="Last interaction timestamp")

class BriefRequest(BaseModel):
    topic: str = Field(..., description="Research topic")
    depth: int = Field(3, ge=1, le=5, description="Research depth level (1-5)")
    follow_up: bool = Field(False, description="Whether this is a follow-up query")
    user_id: str = Field(..., description="User identifier for context")