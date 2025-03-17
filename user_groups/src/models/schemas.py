from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class RequestFilterInteraction(BaseModel):
    agent_id: str
    user_type: str
    geography:Optional[List]
    resolution: Optional[List]
    engagement_level: Optional[List]
    dominant_topic: Optional[List]
    avg_sentiment: Optional[List]
    drop_off_sentiments: Optional[List]
    topic:Optional[List]
    sentiment:Optional[List]
    emotion:Optional[List]
    intent:Optional[List]
    risky_behaviour:Optional[List]
    query:Optional[List]
    issue:Optional[List]
    

class CreateGroupResponse(BaseModel):
    status_code: int
    status_message: str
    message :str

class UserGroupTable(BaseModel):
    days:Optional[int]
    iscustom:bool
    start_date:date
    end_date:date 


