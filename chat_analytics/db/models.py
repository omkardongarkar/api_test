from pydantic import BaseModel, Extra
from typing import Generic, List, Dict, TypeVar, Union, Optional
from datetime import datetime, time, timedelta

T = TypeVar("T")

class InteractionResponse(BaseModel):
    sentiment: str
    unique_users_count: int
    unique_conversation_count: int
    unique_interaction_Count: int


class ErrorResponse(BaseModel):
    status_code: int
    detail: str

class InteractionResponse(BaseModel):
    id: str
    parentId: str



class ConversationDetails(BaseModel):
    id: str
    conversation_id : str
    user_id: str
    agent_id: int
    resolution: str
    geography: str
    timestamp:datetime
    engagement_level: str
    dominant_topic: str
    avg_sentiment: str
    drop_off_sentiments: str
    error_rate: int
    dialog_turns: int
    duration:int 
    class Config:
        extra = Extra.allow 
    
class ConversationResponse(BaseModel):
    status_code: int
    message: str
    data : ConversationDetails

class InteractionDetails(BaseModel):
    id:str
    conversation_id:str
    interaction_id:int
    user_id: str
    agent_id:int
    message_id: str
    role: str
    bot_id: str
    intent: str
    sentiment: str
    topic: str
    emotion: str
    error_value: int
    error_reason: str
    risky_behaviour: str
    query: str
    issue: int
    keywords: str
    timestamp:datetime

class InteractionResponseModel(BaseModel,Generic[T]):
    status_code: int
    message: str
    data : T

class InteractionData(BaseModel):
    all_users_count:int
    is_boolean_true_count:int
    category:str
    unique_users_count:int
    unique_conversation_count:int
    unique_interaction_Count:int
    conversation_ids:List[str]
    user_ids:List[str]
    interaction_ids:List[str]
    retention_in_percentage:float
    error_rate:float
    total_interactions:int
    interaction_percentage:float
    user_percentage:float

class InteractionTable(BaseModel):
    status_code: int
    message:str
    data:List[InteractionData]


class InteractionTableRequest(BaseModel):
    category:str
    agent_id:str
    days: int

class ResponseInteractionTrend(BaseModel):
    status_code: int
    message:str
    class Config:
        extra = Extra.allow 

class RequestFilterInteraction(BaseModel):
    category:str
    geography:Optional[List]
    resolution: Optional[List]
    engagement_level: Optional[List]
    dominant_topic: Optional[List]
    avg_sentiment: Optional[List]
    drop_off_sentiments: Optional[List]
    agent_id: int
    topic:Optional[List]
    sentiment:Optional[List]
    emotion:Optional[List]
    intent:Optional[List]
    risky_behaviour:Optional[List]
    query:Optional[List]
    issue:Optional[List]
    days:int


class GetInteractionId(BaseModel):
    interaction_id:str