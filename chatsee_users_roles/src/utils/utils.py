# utils.py

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from common.database import db,user_collections
from bson import ObjectId

SECRET_KEY = "your_secret_key"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    # agents_list = await agent_collection.find({},{"_id": 1, "agent_name": 1, "status": 1}).to_list(length=None)
    user = await user_collections.find_one({"email": username})


    print(username)
    return user

async def get_role(role_id: ObjectId):
    role = await db.roles.find_one({"_id": role_id})
    return role

async def get_agent(agent_id: ObjectId):
    agent = await db.agents.find_one({"_id": agent_id})
    return agent

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def decode_token(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise credentials_exception