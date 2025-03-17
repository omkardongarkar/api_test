

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from common.constants import Messages, StatusCode
from common.database import get_db,agent_collection
from common.utils import serialize_mongo_document
from dashboard_metadata.src.db.schemas import AgentResponse, AgentsList, ErrorResponse, FilteMetadata


router = APIRouter(prefix="/dashboard_metadata", tags=["dashboard"])

@router.post("/get_metadata",response_model=FilteMetadata,responses={500: {"model": ErrorResponse}})
async def get_unique_values( db: AsyncIOMotorDatabase = Depends(get_db)):
    
    
    try:
    
        result = await db["filter_metadata_view"].find_one({})
        if result is None:
            raise HTTPException(status_code=500, detail="Something went wrong")
        # print(result)


        return FilteMetadata(
                status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, result=result
            )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status_code": 500, "message": f"Internal Server Error: {str(e)}"}
        )
    

@router.post("/get_dashboard",response_model=FilteMetadata,responses={500: {"model": ErrorResponse}})
async def dashboard_conversation( db: AsyncIOMotorDatabase = Depends(get_db)):
    
    
    try:
    
        result = await db["conversation_metadata_view"].find_one({})
        if result is None:
            raise HTTPException(status_code=500, detail="Something went wrong")
        # print(result)

        # return result


        return FilteMetadata(
                status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, result=result
            )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status_code": 500, "message": f"Internal Server Error: {str(e)}"}
        )
    

@router.post("/agents_list", response_model=AgentResponse)
async def get_agent_list(db:AsyncIOMotorDatabase = Depends(get_db)):
    """
    This endpoint is used to fetch agents and its details
    """
    # logger.info(f"Requesting for agent details list ")
    try:
        agents_list = await agent_collection.find({},{"_id": 1, "agent_name": 1, "status": 1}).to_list(length=None)
    
        result= serialize_mongo_document(agents_list) 
       
        return AgentResponse(
                status_code=StatusCode.SUCCESS, message=Messages.SUCCESS, data=result
            )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status_code": 500, "message": f"Internal Server Error: {str(e)}"}
        )
    
    
    
    