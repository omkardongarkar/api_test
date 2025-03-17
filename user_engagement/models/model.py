from beanie import Document
from bson import ObjectId
from pydantic import Field
from datetime import datetime
from typing import Optional



class Conversation(Document):
    id: Optional[str] = Field(alias="_id")
    conversation_id : str= Field(...)
    user_id: str= Field(...)
    agent_id: int= Field(...)
    resolution: str= Field(...)
    geography: str= Field(...)
    timestamp:datetime= Field(...)
    engagement_level: str= Field(...)
    dominant_topic: str= Field(...)
    avg_sentiment: str= Field(...)
    drop_off_sentiments: str= Field(...)
    error_rate: int= Field(...)
    dialog_turns: int= Field(...)
    duration:int= Field(...)
    class Settings:
        collection = "conversations"
    class Config:
        json_encoders = {ObjectId: str} 