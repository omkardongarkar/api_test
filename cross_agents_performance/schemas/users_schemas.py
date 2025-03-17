from typing import List, Optional
from pydantic import BaseModel


class RequestUsers(BaseModel):
    geography:Optional[List]
    resolution: Optional[List]
    engagement_level: Optional[List]
    dominant_topic: Optional[List]
    avg_sentiment: Optional[List]
    drop_off_sentiments: Optional[List]
    agent_ids: Optional[List]
    topic:Optional[List]
    sentiment:Optional[List]
    emotion:Optional[List]
    intent:Optional[List]
    risky_behaviour:Optional[List]
    query:Optional[List]
    issue:Optional[List]
    days:int