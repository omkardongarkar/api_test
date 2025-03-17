import time
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from app_logging.logger import logger
from common.database import get_db, init_db
from common.constants import Messages, StatusCode

from common.utils import serialize_mongo_document
from cross_agents_performance.api.daily_users import count_users_daily
from cross_agents_performance.api.monthly_sessions import get_sessions_monthly
from cross_agents_performance.schemas.agents_schemas import ResponseAgents
from app_logging.logger import logger
from cross_agents_performance.schemas.users_schemas import RequestUsers

from cross_agents_performance.api.resolution_rate import all_agents_resolution_rate
from cross_agents_performance.views.issue_monthwise import get_issues_monthly_count, get_top_issue_query_resolution
router = APIRouter( tags=["Cross Agents Performance"])



@router.post("/agents_details")#, response_model=List[Agents])
async def get_agent_details(db:AsyncIOMotorDatabase = Depends(get_db)):
    """
    This endpoint is used to fetch agents and its details
    """
    logger.info(f"Requesting for agent details list ")
    agents_list = await db["agents"].find({}).to_list()
    
    result= serialize_mongo_document(agents_list)  # to convert objectID into str
    if not agents_list:
        raise HTTPException(status_code=404, detail="No agents_list found")
    logger.info(f"Returning Agent and its details ")
    return result


@router.post("/agents_daily_users")
async def get_daily_users_for_agents(request:RequestUsers,db:AsyncIOMotorDatabase=Depends(get_db)):

    """
    This api is used to fetch all users for all agents with filters
    """

    results= await count_users_daily(request,db)
    print(results)

    # result={"ping":"pong"}
    return results


@router.post("/agents_session_handled")
async def get_monthly_session_handles(request:RequestUsers,db:AsyncIOMotorDatabase=Depends(get_db)):

    """
    This api is used to fetch all users for all agents with filters
    """
    s_time= time.time()
    results= await get_sessions_monthly(request,db)
    e_time = time.time()
    print(results)

    print("Time Required: ",e_time-s_time)

    # result={"ping":"pong"}
    return results

@router.post("/all_agents_resolution_rate")
async def agents_resolution_rate(request:RequestUsers,db:AsyncIOMotorDatabase=Depends(get_db)):

    """
    This api is used to fetch to find resolution of all_agents and filter condition
    """
    try:
        logger.info("Finding resolution rate for all agents")

        results= await all_agents_resolution_rate(request,db)
    
    
        return results


    except Exception as e:
        
        logger.error(f"Error for finding agent resolution : {e}")
        return JSONResponse(
            status_code=500,
            content={"status_code": 500, "message": f"Internal Server Error: {str(e)}"}
        )
    

@router.post("/get_monthly_issue_count")
async def get_monthly_issue_count(request:RequestUsers,db:AsyncIOMotorDatabase=Depends(get_db)):

    """
    This api is to get monthly issue count
    """
    s_time= time.time()
    results= await get_issues_monthly_count(request,db)
    e_time = time.time()
    print(results)

    print("Time Required: ",e_time-s_time)

    # result={"ping":"pong"}
    return results


@router.post("/get_top_issue_and_query")
async def get_top_issue_and_query(request:RequestUsers,db:AsyncIOMotorDatabase=Depends(get_db)):

    """
    This api is to get monthly issue count
    """
    s_time= time.time()
    results= await get_top_issue_query_resolution(request,db)
    e_time = time.time()
    # print(results)

    print("Time Required: ",e_time-s_time)

    # result={"ping":"pong"}
    return results