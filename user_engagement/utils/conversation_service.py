import json
from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId, errors
from common.constants import Messages, StatusCode
from common.utils import serialize_mongo_document
from user_engagement.models.model import Conversation
# from user_engagement.schemas.schemas import ResponseConversationUserFlow
# from user_interaction.model.schemas import ResponseConversationUserFlow
from collections import Counter, defaultdict
from pymongo.errors import PyMongoError
from app_logging.logger import logger

async def convert_mongo_doc(doc):
    """Convert ObjectId to string in MongoDB document."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def get_conversations(request,db):
    """Fetch paginated conversation """
    cutoff_date = datetime.utcnow() - timedelta(days=request.days)
    
    query = {"agent_id":ObjectId( request.agent_id), "timestamp": {"$gte": cutoff_date}}

    try:

        conversations = (
            await db["conversations"]
            .find(query)
            .sort("timestamp", -1)  # 
            .limit(request.limit)
            .to_list(length=request.limit)
        )

        if not conversations:
            raise HTTPException(status_code=404, detail="Document not found")

        print(conversations)

        for conversation in conversations:
            conversation["_id"] = str(conversation["_id"])
            conversation["agent_id"] = str(conversation["agent_id"])
            # conversation["conversation_id"] = str(conversation["conversation_id"])

        
        total_count = await db["conversations"].count_documents(query)

        

        no_of_drop_off = Counter(conversation["dialog_turns"] for conversation in conversations if "dialog_turns" in conversation)
        
        sorted_no_of_drop_off = dict(sorted(no_of_drop_off.items()))

        cutoff_date = datetime.utcnow() - timedelta(days=request.days)

        
        

        
        
        
        return conversations, sorted_no_of_drop_off

    except PyMongoError as e:
        # Catch MongoDB-related errors
        raise HTTPException(status_code=500, detail=f"MongoDB error: {str(e)}")
    except Exception as e:
        # Catch general errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
   

async def get_user_retention_percentage(request,db):

    """
    this function is used to get user retanetion and its percentage weekly based on agent id and
    number of days.
    It will return no of weekly no of users and its retention
    """
    # logger(f"calculating user retention percentage for last {request.days}")

    # To get last date to fetch data
    cutoff_date = datetime.utcnow() - timedelta(days=request.days)


    # Create mongo db query to be executed on data
    query = {"agent_id": ObjectId(request.agent_id), "timestamp": {"$gte": cutoff_date}}

    # logger.info(f"Query is : {query}")

    
    # Fetch the data from mongodb
    conversations = await db["conversations"].find(query).to_list(None)
    
        

    # To convert BSON IDs into string
    for interaction in conversations:
        interaction["_id"] = str(interaction["_id"])    


    # To find  users per week
    users_per_week = count_users_on_each_week(conversations)
        
        
        
    # to calculate retention
    result=calculate_retention(users_per_week)

    return result



def count_users_on_each_week(conversations):
    """Group interactions by week and count runs"""
    users_per_week = defaultdict(Counter)


    try:
        logger.info(f" grouping interactions and its percentage per week")

        for conversation in conversations:
            date_format=conversation["timestamp"]
            i_year = date_format.year
            i_month = date_format.month
            week_number = conversation["timestamp"].isocalendar()[1]
            return_week_keyname=f"{i_year}_{i_month}_{week_number}"  # Get ISO week number
            users_per_week[return_week_keyname][conversation["user_id"]] += 1  # Count runs

        return {week: dict(sorted(runs.items())) for week, runs in sorted(users_per_week.items())}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid conversations data ")

def calculate_retention(users_per_week):


    """
    This method finds user retention per week 

    It takes weekly user list, find unoques users, length and no of users retained per week

    It finds unbers of users, percetage, length and no of users retained per week

    """
    
    # arrange weeks in ascending order
    week_keys = sorted(users_per_week.keys())

    
    return_data={}

    for i in range(len(week_keys) - 1):
        key = f"week_{i}"
        
        return_data[key]=[]

        # To get current week
        current_week = week_keys[i]
        current_users = set(users_per_week[current_week].keys())
        
        # To get total number of users for that week
        Total_users=len(users_per_week[current_week].keys())
        
        total_users={"Total_users":Total_users}
        return_data[key].append(total_users)
       
        # To find retention percentage on each week
        return_data[key].append({"Retention_Percentage":(Total_users/Total_users)*100}) # 
        # return_data[key].append({"Retention_Percentage":(Total_users/Total_users)*100})

        # Append current week details in return data
        return_data[key].append({"week_date":current_week})
        for j in range(i + 1, len(week_keys)):
            next_week = week_keys[j]
            next_runs = set(users_per_week[next_week].keys())

            repeated_users = current_users.intersection(next_runs)

            percentage_of_repetation = (len(repeated_users)/len(current_users))*100

            return_data[key].append({f"week_{j}":percentage_of_repetation})

            
    # To get last week details
    if week_keys:
        key = f"week_{i}"
        return_data[key].append(total_users)
        return_data[key].append({"Retention_Percentage":(Total_users/Total_users)*100})


    return return_data


async def get_user_interactions(db,agent_id,page,page_size):
    if agent_id:
        print("pass")
        try:
            agent_match = {"agent_id": ObjectId(agent_id)}

            logger.info(f" match condition is {agent_match} to retrive data ")

        except errors.InvalidId:  # Catch specific MongoDB ObjectId error
            raise HTTPException(status_code=400, detail="Invalid ObjectId format1")

        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    try:
        skip = (page-1) * page_size
        skip = 1

        print(skip)

        logger.info(f" Creating a query to fetch required data")

        query =await get_query_user_interaction(agent_match,skip,page_size)

        
        
        logger.info(f" Query  generation to fetch data is completed")
        
        result = await db["conversations"].aggregate(query).to_list(length=1)
        
        
        if not result or not result[0]['data'] or not result[0]['total_count']:
            
            logger.info(f" No specific document found from database")
            
            raise HTTPException(status_code=404, detail="Document not found")

        
        result= serialize_mongo_document(result) # to convert ObjectId into string

    # Extract results and total count
        data = result[0].get("data", [])
        total_count = result[0].get("total_count", [{}])[0].get("count", 0)

        return total_count,data
    except Exception as e:
        # Catch general errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

async def get_query_user_interaction(agent_match,skip,page_size):
    query = [
        {
        "$lookup": {
            "from": "interactions",  
            "localField": "_id",  
            "foreignField": "conversation_id",  
            "as": "interaction_docs"
					}
		},
        {
        "$addFields": {
            "interaction_count": { "$size": "$interaction_docs" },  
            "interaction_ids": { 
                "$map": { 
                    "input": "$interaction_docs",
                    "as": "doc",
                    "in": "$$doc._id" 
                }
            }
			}
		},
        {
        "$match":agent_match
        
		},
                            
        {
        
		"$facet": {
            "data": [
				{ "$skip": skip},
				{ "$limit":page_size },
        {
        "$project": {
            "_id": 1,
            "interaction_name": 1,  
            "agent_id": 1,  
            "interaction_count": 1,
            "interaction_ids": 1
        }
        }
            ],
            "total_count": [
                    { "$count": "count" }
            ]
        }
        }                    
                                
            
        

        
    ]

    return query