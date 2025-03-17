from pydantic import BaseModel, Extra
from typing import Generic, List, Dict, TypeVar, Union, Optional
from datetime import datetime, time, timedelta

class ResponseAgents(BaseModel):
    id: Optional[str] 
    agent_name: str 
    agent_type: str 
    department_owner: str 
    status: bool 
    audience: str 
    risk_score: float 
    created_at: datetime 
    modified_at: datetime 
    is_deleted: bool 
