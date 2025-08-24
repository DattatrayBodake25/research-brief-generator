from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel
from ..models.schemas import BriefRequest, FinalBrief
from ..core.graph import research_graph
from ..utils.logger import logger

router = APIRouter()

# In-memory storage for demo (replace with proper DB)
active_requests: Dict[str, Any] = {}

@router.post("/brief", response_model=Dict[str, Any])
async def generate_brief(request: BriefRequest, background_tasks: BackgroundTasks):
    """Generate a research brief"""
    try:
        # Create initial state
        request_id = str(uuid.uuid4())
        
        state = {
            "topic": request.topic,
            "depth": request.depth,
            "user_id": request.user_id,
            "follow_up": request.follow_up,
            "current_step": "start"
        }
        
        # Store request metadata
        active_requests[request_id] = {
            "status": "processing",
            "start_time": datetime.now(),
            "request": request.model_dump()
        }
        
        # Execute graph in background
        background_tasks.add_task(
            execute_research_workflow,
            request_id,
            state
        )
        
        return {
            "brief_id": request_id,
            "topic": request.topic,
            "status": "processing",
            "message": "Research started in background"
        }
        
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brief/{brief_id}")
async def get_brief_status(brief_id: str):
    """Get status of a research brief"""
    if brief_id not in active_requests:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    return active_requests[brief_id]

async def execute_research_workflow(request_id: str, initial_state: Dict[str, Any]):
    """Execute the research workflow"""
    try:
        # Execute the graph
        final_state = await research_graph.ainvoke(initial_state)
        
        # Update request status
        if final_state.get("final_brief"):
            active_requests[request_id].update({
                "status": "completed",
                "result": final_state["final_brief"].model_dump(),
                "end_time": datetime.now(),
                "errors": final_state.get("errors", [])
            })
        else:
            active_requests[request_id].update({
                "status": "failed",
                "end_time": datetime.now(),
                "errors": final_state.get("errors", ["Unknown error"])
            })
            
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        active_requests[request_id].update({
            "status": "failed",
            "end_time": datetime.now(),
            "errors": [str(e)]
        })