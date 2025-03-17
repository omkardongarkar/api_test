import time
from bson import ObjectId
from fastapi import APIRouter, FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from common.constants import VIEW_CREATE_CONSTANT_STRING, Messages, StatusCode
from user_groups.src.api.create_views import create_view_in_db
from user_groups.src.api.fetch_table import get_table_data, get_trend_data
from user_groups.src.models.schemas import  CreateGroupResponse, RequestFilterInteraction, UserGroupTable
from common.database import get_db,user_type_group
from pymongo.errors import PyMongoError
router = APIRouter(prefix="/user_group", tags=["User_groups"])






@router.post("/create_user_group",response_model=CreateGroupResponse)
async def create_group(request: RequestFilterInteraction,db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        existing_group = await user_type_group.find_one({"agent_id":ObjectId(request.agent_id), "user_type": request.user_type})
        if existing_group:
            raise HTTPException(status_code=400, detail="Group name already exists for this user")
        document = request.dict()
        document["agent_id"] = ObjectId(document["agent_id"]) 

        pipeline = create_view_in_db(request,db)
        try:
            response=await db.command({
            "create": VIEW_CREATE_CONSTANT_STRING +request.user_type,  # Name of the view
            "viewOn": "interactions",  # Base collection for the view
            "pipeline": pipeline  # Aggregation pipeline
        })
    
        
        except PyMongoError as e:
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=f"Problems in creating views: {e}",
            )
        
         
        result =await db["user_type_groups"].insert_one(document)

        return CreateGroupResponse(status_code=StatusCode.CREATED,status_message=Messages.CREATED,message=f"User Group Created {request.user_type} ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_user_groups_table")
async def get_user_groups( request:UserGroupTable,db: AsyncIOMotorDatabase = Depends(get_db),):
    groups = await user_type_group.find({},{"_id":0,"agent_id":1,"user_type":1}).to_list(None)


    
    
    if not groups:
        return {"message": "No groups found"}
    stime=time.time()
    data= await get_table_data(groups,db,request.days)
    etime=time.time()

    print("total: ",etime-stime)
    return {"data": data}

@router.post("/get_user_groups_trend")
async def get_user_groups( request:UserGroupTable,db: AsyncIOMotorDatabase = Depends(get_db),):
    
    groups = await user_type_group.find({},{"_id":0,"agent_id":1,"user_type":1}).to_list(None)




    
    
    if not groups:
       return {"message": "No groups found"}
    stime=time.time()
    data= await get_trend_data(groups,db,request)
    etime=time.time()

    print("total: ",etime-stime)
    return {"data": data}


@router.delete("/delete_user_group/{group_name}")
async def delete_group(group_name: str,db: AsyncIOMotorDatabase = Depends(get_db)
):
    
    existing_group = await user_type_group.find_one({"user_type": group_name})

    print(existing_group)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group not found")

    view_name = existing_group.get("user_type")  # Assuming the view name is stored in the document
    print(view_name)

    # Drop the view from MongoDB
    if view_name:
        complete_view_name=VIEW_CREATE_CONSTANT_STRING+view_name
        try:
            await db.command({"drop": complete_view_name})  # Drops the MongoDB view
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to drop view: {str(e)}")

    
    delete_result = await  user_type_group.delete_one({"_id": existing_group.get("_id")})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete group")

    return {"status_code":204,"message": "Group and associated view deleted successfully"}



