from beanie import Document, PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field, root_validator
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import bcrypt
import os
from datetime import datetime

# User Model




class Users(Document):
    _id: PydanticObjectId
    username: str
    email: EmailStr
    password_hash: str
    role_id: PydanticObjectId  # Reference to Role
    assigned_projects: Optional[List[PydanticObjectId]] = []  

    class Settings:
        name = "users"

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    @classmethod
    def hash_password(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

class SingleUsers(Document):
    
    _id: PydanticObjectId
    username: str
    role_id: PydanticObjectId
    assigned_projects: Optional[List[PydanticObjectId]] = []

    class Settings:
        name = "users"


class Role(Document):
    name: str
    class Settings:
        name = "roles"

# Project Model
class Agent(Document):
    agent_name: str
    

    class Settings:
        name = "agents"

# User Registration Schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: str
    assigned_agents: Optional[List[str]] = []
    created_on: datetime = Field(default_factory=datetime.utcnow)  
    modified_on: datetime = Field(default_factory=datetime.utcnow) 
    is_deleted: bool = False

# Response Schema
class UserResponse(BaseModel):
    status_message :str
    status_code : int
    
    
class USerAllList(BaseModel):
    
    id: str
    username: str
    email:str
    role: dict  
    assigned_agents: List[dict]

class AllUserResponse(BaseModel):
    status_code:int
    status_message:str
    data:List[dict]



# Projection Model
class FetchUsers(BaseModel):
    id: PydanticObjectId
    username: str
    role_id: PydanticObjectId
    assigned_projects: Optional[List[PydanticObjectId]] = []

    class Config:
        
        json_encoders = {
            PydanticObjectId: str
        }
    @root_validator(pre=True)
    def handle_id(cls, values):
        if '_id' in values:
            values['id'] = values.pop('_id')
        return values
 

class SingleUserResponse(BaseModel):

    id: str
    username: str
    role: Optional[dict] = None
    assigned_projects: List[dict] = []




class UserLogin(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    username: str
    password_hash: str
    role_id: ObjectId
    assigned_projects: List[ObjectId]





class UserToken(BaseModel):
    status_code:int
    status_message:str
    model_config = ConfigDict(arbitrary_types_allowed=True)
    access_token: str
    

class TokenData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    username: Optional[str] = None
    role: Optional[str] = None
    assigned_projects: Optional[List[str]] = None