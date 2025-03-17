from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status
from beanie import init_beanie

# from conversation_details.database.models import Conversation

from user_engagement.models.model import Conversation
MONGO_URI = "mongodb://localhost:27017/Chatsee"  # Replace with your URI

try:
    client = AsyncIOMotorClient(MONGO_URI) #Motor Client
    db = client.get_default_database() # Gets the database from URI


    agent_collection = db["agents"]
    conversations_collection = db["conversations"]
    interactions_collection = db["interactions"]
    user_collections= db.users
    role_collections= db["roles"]
    user_type_group=db["user_type_groups"]
    collections =  db.list_collection_names()
    print(f"✅ Available collections: {collections}")




    print("Connected to MongoDB (Motor)")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")





async def init_db():
    """Initialize Beanie with the database."""
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["Chatsee"]

    # Debugging: Print available collections
    collections = await db.list_collection_names()
    print(f"✅ Available collections: {collections}")

    await init_beanie(database=db, document_models=[Conversation])
    
   
    # await init_beanie(database=db, document_models=[Agents])

async def get_db():  # Dependency function to access the database (async)
    try:
        yield db
    finally:
        pass  # You can add cleanup code here if needed