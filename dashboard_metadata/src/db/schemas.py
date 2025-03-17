

from typing import List
from pydantic import BaseModel, Field

class InteractionsMetadata(BaseModel):
    sentiments: List[str]
    emotions :List[str]
    topics: List[str]
    intents: List[str]



class ConversationsMetadata(BaseModel):
    geographies:List[str]
    resolutions: List[str]
    engagement_levels:List[str]




class FilteMetadata(BaseModel):
    status_code: int
    message : str
    result : dict
    class Config:
        orm_mode = True
    
class ErrorResponse(BaseModel):
    status_code: int
    message: str

class AgentsList(BaseModel):
    id: str = Field(alias="_id") 
    agent_name: str
    status : bool


class AgentResponse(BaseModel):
    status_code : int
    message : str
    data : List[AgentsList]