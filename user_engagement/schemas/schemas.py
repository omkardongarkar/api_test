
from pydantic import BaseModel, Extra
from typing import Generic, List, Dict, TypeVar, Union, Optional
from datetime import datetime, time, timedelta



class RequestConversation(BaseModel):
    agent_id: str
    days: int
    page: int
    limit:int

class RequestUserRetention(BaseModel):
    agent_id: str
    days: int


class RequestUserInteraction(BaseModel):
    agent_id: str
    page: int
    page_size : int
    


class ConversationUserFlow(BaseModel):
    _id: str
    # conversation_id: str
    user_id: str
    agent_id: str
    resolution: str
    geography: str
    timestamp: datetime
    engagement_level: str
    dominant_topic: str
    avg_sentiment: str
    drop_off_sentiments: str 
    error_rate: int
    dialog_turns: int
    duration: int




class ResponseUserInteraction(BaseModel):
    status_code :int    
    status_message: str
    total_count : int
    page : int
    page_size: int
    total_pages : int
    data : List[Dict]

    

class ResponseConversationUserFlow(BaseModel):
    status_code :int    
    status_message: str
    data: List[ConversationUserFlow]
    drop_off_count : Dict[int,int]
    # total : int
    # page : int
    # limit : int
    # total_pages :int


class UserRetentionResponse(BaseModel):
    status_code :int    
    status_message: str
    data: Dict[str,List]