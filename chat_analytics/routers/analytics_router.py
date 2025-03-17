import json
import os
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any, Dict, List, Optional
from common.database import get_db
from chat_analytics.db.models import InteractionResponse, ErrorResponse
from datetime import datetime, timedelta
from chat_analytics.db.models import(
ConversationDetails,
    ConversationResponse,
    GetInteractionId,
    InteractionDetails,
    InteractionResponseModel,
    InteractionTable,
    InteractionTableRequest,
    RequestFilterInteraction,
    ResponseInteractionTrend,
)

from common.constants import CHAT_DATA_EXTENSION, CHAT_FILENAME_INITIAL, StatusCode, Messages,CHAT_DATA_STORAGE_PATH
from app_logging.logger import logger


from chat_analytics.services.service import fetch_conversation_data, fetch_interactions_on_ids, get_filtered_interactions, get_interaction_filtered_trend_data, get_interaction_table_data, get_interaction_trend_data



router = APIRouter(prefix="/interactions", tags=["Chat_Analytics"])


@router.post(
    "/get_filtered_interaction_table",
    response_model=InteractionTable,
    responses={500: {"model": ErrorResponse}},
)
async def get_filtered_interaction_table(
    request: RequestFilterInteraction,
    db: AsyncIOMotorDatabase = Depends(get_db),  # Type hint for Motor database
):

    
    try:

        result_data = await get_filtered_interactions(request,db)
 
        return InteractionTable(
            status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, data=result_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"No valid interaction_ids provided: {e}",
        )


@router.post("/fetch_interaction_table", responses={500: {"model": ErrorResponse}})
async def fetch_interaction_table(
    request: InteractionTableRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):

    try:
        

        result_data = await get_interaction_table_data(request,db)

        return InteractionTable(
            status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, data=result_data
        )

        # return results
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"No valid interaction_ids provided: {e}",
        )
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@router.post("/fetch_interaction_trend", responses={500: {"model": ErrorResponse}})
async def fetch_interaction_trend(
    request: InteractionTableRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    

    try:
        
        daywise_data = await get_interaction_trend_data(request,db)

        

        return ResponseInteractionTrend(
            status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, data=daywise_data
        )
        # return results
    except Exception as e:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"No valid interaction_ids provided: {e}",
        )
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@router.post(
    "/get_filtered_interaction_trend", responses={500: {"model": ErrorResponse}}
)
async def get_filtered_interaction_trend(
    request: RequestFilterInteraction,
    db: AsyncIOMotorDatabase = Depends(get_db),  # Type hint for Motor database
):

    logger.info(f">>>>>> datewise {request.category} for trends finding started <<<<<<")
    

    

    try:
        
        daywise_data = await get_interaction_filtered_trend_data(request,db)

        logger.info(f">>>>>> datewise {request.category} trends finding ends <<<<<<")

        return ResponseInteractionTrend(
            status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, data=daywise_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"No valid interaction_ids provided: {e}",
        )


@router.post(
    "/get_interctions_details", response_model=InteractionResponseModel[Dict[str, Any]]
)
async def get_interctions_details(
    InteractionIds: list[str], db: AsyncIOMotorDatabase = Depends(get_db)
):

    response_data= await fetch_interactions_on_ids(InteractionIds,db)
    # Return standardized response
    return InteractionResponseModel(
        status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, data=response_data
    )


@router.post(
    "/get_conversation_details", response_model=ConversationResponse
)
async def get_conversation_details(
   request:GetInteractionId, db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch parent details from child_id"""
    try:
     conversation_details=await fetch_conversation_data(request,db)

     return ConversationResponse(
        status_code=StatusCode.SUCCESS,
        message=Messages.SUCCESS,
        data=ConversationDetails(
            id=conversation_details["_id"], **conversation_details
        )
        ) 
    except Exception as e: # Catch other potential errors
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"JSON File not readable: {e}",
        )
    


    
