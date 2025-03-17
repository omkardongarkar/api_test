from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from motor.motor_asyncio import AsyncIOMotorDatabase

from common.constants import Messages, StatusCode
from common.database import get_db
# from app.services.interaction_service import fetch_interactions
# from user_interaction.db import get_db
from common.utils import serialize_mongo_document
from user_engagement.schemas.schemas import RequestConversation, RequestUserInteraction,RequestUserRetention,ResponseConversationUserFlow, ResponseUserInteraction,UserRetentionResponse
from user_engagement.utils.conversation_service import  get_conversations, get_user_interactions, get_user_retention_percentage
from app_logging.logger import logger
# .db import get_db

router = APIRouter()

@router.post("/get_conversation_underflow",response_model=ResponseConversationUserFlow)
async def get_interactions(
    request:RequestConversation, db:AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch conversation with  pagination, and date filtering"""
    # return await fetch_conversations(request,db)

    try:


        result, no_of_drop_off= await get_conversations(request,db)
    
        return  ResponseConversationUserFlow(
                status_code=StatusCode.SUCCESS, status_message=Messages.SUCCESS, data=result, drop_off_count=no_of_drop_off
            )
    except Exception as e:
        # Catch general errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/fetch_user_weekly_and_retention",response_model=UserRetentionResponse)
async def get_user_retention(
    request:RequestUserRetention, db:AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch user retention, user retention per week """
    logger.info(f"finding user retention and its percentage ")

    try:


        result= await get_user_retention_percentage(request,db)

        logger.info(f"Responding completed user retention and its percentage  ")       
        return UserRetentionResponse(
                status_code=StatusCode.SUCCESS, status_message=Messages.SUCCESS, data=result
            )
    
    

    except Exception as e:
        # Catch general errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    



@router.post("/fetch_all_users_interactions",response_model=ResponseUserInteraction)
async def fetch_user_interaction(
    request:RequestUserInteraction, db:AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch user retention, user retention per week """

    logger.info(f">>>>>> Started User Interaction   <<<<<<")

    agent_id = request.agent_id
    page = request.page
    page_size = request.page_size

    agent_match = {}

    try:

        total_count, data =await get_user_interactions(db,agent_id,page,page_size)


        logger.info(f" valid data is returned from api ")

        return ResponseUserInteraction (
            status_code =StatusCode.SUCCESS, 
            status_message=Messages.SUCCESS,
            total_count = total_count,
            page = page,
            page_size = page_size,
            total_pages = (total_count + page_size - 1), 
            data = data
        )

    except Exception as e:
        # Catch general errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")