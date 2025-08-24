import json
import aiofiles
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from .schemas import FinalBrief, UserContext
from ..utils.logger import logger

class UserHistoryManager:
    """Manages user research history storage"""
    
    def __init__(self, storage_path: str = "data/user_history"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get user history file path"""
        return self.storage_path / f"{user_id}.json"
    
    async def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's research history"""
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            return []
        
        try:
            async with aiofiles.open(user_file, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else []
        except Exception as e:
            logger.error(f"Error reading user history: {e}")
            return []
    
    async def save_brief(self, user_id: str, brief: FinalBrief) -> bool:
        """Save a brief to user history"""
        try:
            history = await self.get_user_history(user_id)
            
            # Create summary for storage
            brief_summary = {
                "brief_id": brief.brief_id,
                "topic": brief.topic,
                "executive_summary": brief.executive_summary,
                "generated_at": brief.generated_at.isoformat(),
                "references_count": len(brief.references)
            }
            
            history.append(brief_summary)
            
            # Keep only last 10 briefs
            if len(history) > 10:
                history = history[-10:]
            
            async with aiofiles.open(self._get_user_file(user_id), 'w') as f:
                await f.write(json.dumps(history, indent=2))
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving brief: {e}")
            return False