
from datetime import datetime, timedelta
import json
import os
from typing import Dict
from bson import ObjectId
from fastapi import Depends, HTTPException
from chat_analytics.db.models import InteractionDetails, InteractionTableRequest
from chat_analytics.services.aggeregation import add_conversation_field, extract_retention_percentage, get_conversation_fields_post, get_conversation_query, get_data_from_db, get_interaction_filter_query, group_by_date_query, organise_data_datewise, primary_filter_aggeregation, primary_filter_condition
from common.constants import CHAT_DATA_EXTENSION, CHAT_DATA_STORAGE_PATH, CHAT_FILENAME_INITIAL, StatusCode
from common.database import get_db
from app_logging.logger import logger

async def get_interaction_table_data(
    request,db):
    """
    This Method is used to fetch data from db based on interaction category like sentimen, topic etc..
    It returns numbers of user , its percentage , retention and number of interactions
    """

    # Get requested data into individual varibales
    category = request.category
    agent_id = request.agent_id
    days = request.days
    logger.info(
        f">>>>>>>>>>>           Started {category} for  analytics for table generation           <<<<<<<<<<"
    )

    combined_match_criteria = {}
    if days:
        filter_date = datetime.utcnow() - timedelta(days=days)
    combined_match_criteria["agent_id"] = (
            ObjectId(agent_id)  # reuired it to filter result based on agent_id
    )
    combined_match_criteria["timestamp"] = {
        "$gte": filter_date
    }  # reuired it to filter result based on agent_id
    agg_pipeline = []

    # create a filter query string based on combined_match_criteria
    agg_pipeline = primary_filter_condition(combined_match_criteria, agg_pipeline)

    # create a query string based on category reuested
    agg_pipeline = primary_filter_aggeregation(agg_pipeline, category)

    print(agg_pipeline)


    results = await db.interactions.aggregate(agg_pipeline).to_list(None)
    print(results)

    result_data = await extract_retention_percentage(results)

    
   
    return result_data


async def get_filtered_interactions(request,db):
    days = request.days
    match_criteria: Dict[str, any] = {}
    if days:
        filter_date = datetime.utcnow() - timedelta(days=days)

    combined_match_criteria, has_interaction_filters = get_interaction_filter_query(
        request.topic,
        request.sentiment,
        request.emotion,
        request.issue,
        request.query,
        request.risky_behaviour,
        request.intent,
    )

    if request.agent_id is not None:
        combined_match_criteria["agent_id"] = request.agent_id
    if filter_date is not None:
        combined_match_criteria["timestamp"] = {"$gte": filter_date}
    has_interaction_filters = any(
        value is not None for value in combined_match_criteria.values()
    )

    has_conversation_filters = False

    filter_fields = get_conversation_fields_post(
        request.geography,
        request.resolution,
        request.engagement_level,
        request.dominant_topic,
        request.avg_sentiment,
        request.drop_off_sentiments,
    )
    has_conversation_filters = any(
        value is not None for value in filter_fields.values()
    )
    # print("has_conversation_filters",has_conversation_filters)
    pipeline = []

    if has_conversation_filters:
        match_criteria = {"$and": []}

        match_criteria, has_conversation_filters = add_conversation_field(
            filter_fields, match_criteria
        )
        pipeline = get_conversation_query(pipeline)

        if (
            not match_criteria
        ):  # If no match criteria is provided, we add an empty match criteria, so that all the documents are passed.
            match_criteria = {}

        pipeline.append({"$match": match_criteria})

    if has_interaction_filters:
        # print("In has_interaction_filters")
        pipeline.extend(
            [
                {
                    # "$match":interaction_filter_dict
                    "$match": combined_match_criteria
                }
            ]
        )

    pipeline = primary_filter_aggeregation(pipeline, request.category)
    results = await get_data_from_db(db, pipeline)
    result_data = await extract_retention_percentage(results)


    return result_data


async def get_interaction_trend_data(request,db):
    category = request.category
    agent_id = request.agent_id
    days = request.days
    logger.info(
        f">>>>>>>>>>>           Started {category} for  analytics for finding trends of {days}            <<<<<<<<<<"
    )

    combined_match_criteria = {}
    if days:
        filter_date = datetime.utcnow() - timedelta(days=days)

    if request.agent_id is not None:
        combined_match_criteria["agent_id"] = ObjectId(request.agent_id)
    if filter_date is not None:
        combined_match_criteria["timestamp"] = {"$gte": filter_date}
    has_interaction_filters = any(
        value is not None for value in combined_match_criteria.values()
    )
    

    

    # print(match_criteria)

    agg_pipeline = []

    if has_interaction_filters:
        agg_pipeline =primary_filter_condition(combined_match_criteria, agg_pipeline)

    # if days:
    #     filter_date = datetime.utcnow() - timedelta(days=days)
    #     agg_pipeline.append({"$match": {"timestamp": {"$gte": filter_date}}})
    print("agg_pipeline",agg_pipeline)
    agg_pipeline = group_by_date_query(agg_pipeline, category)

    daywise_data = {}
    try:
        results = await get_data_from_db(db, agg_pipeline)
        daywise_data = await organise_data_datewise(results)
        return daywise_data
    except Exception as e:
        return e


async def get_interaction_filtered_trend_data(request,db):


    logger.info(f">>>>>> datewise {request.category} for trends finding started <<<<<<")
    has_conversation_filters = False
    has_interaction_filters = False
    pipeline = []
    match_criteria: Dict[str, any] = {}
    combined_match_criteria, has_interaction_filters = get_interaction_filter_query(
        request.topic,
        request.sentiment,
        request.emotion,
        request.issue,
        request.query,
        request.risky_behaviour,
        request.intent,
    )
    days = request.days
    if days:
        filter_date = datetime.utcnow() - timedelta(days=days)

    if request.agent_id is not None:
        combined_match_criteria["agent_id"] = request.agent_id
    if filter_date is not None:
        combined_match_criteria["timestamp"] = {"$gte": filter_date}
    has_interaction_filters = any(
        value is not None for value in combined_match_criteria.values()
    )
    filter_fields = get_conversation_fields_post(
        request.geography,
        request.resolution,
        request.engagement_level,
        request.dominant_topic,
        request.avg_sentiment,
        request.drop_off_sentiments,
    )
    has_conversation_filters = any(
        value is not None for value in filter_fields.values()
    )

    if has_interaction_filters:

        pipeline = primary_filter_condition(combined_match_criteria, pipeline)

    if has_conversation_filters:
        match_criteria = {"$and": []}

        match_criteria, has_conversation_filters = add_conversation_field(
            filter_fields, match_criteria
        )
        pipeline = get_conversation_query(pipeline)

        if (
            not match_criteria
        ):  # If no match criteria is provided, we add an empty match criteria, so that all the documents are passed.
            match_criteria = {}

        pipeline.append({"$match": match_criteria})

    

    pipeline = group_by_date_query(pipeline, request.category)

    try:
        results = await get_data_from_db(db, pipeline)
        daywise_data = await organise_data_datewise(results)

        logger.info(f">>>>>> datewise {request.category} trends finding ends <<<<<<")

        return daywise_data

    except Exception as e:
        return e 
    
async def fetch_interactions_on_ids(InteractionIds,db):
    response_data = {}

    object_ids = []
    id_mapping = {}  # Store mapping from string ID to ObjectId
    for interaction_id in InteractionIds:
        try:
            object_id = ObjectId(interaction_id)
            object_ids.append(object_id)
            id_mapping[str(object_id)] = interaction_id  # Store original string ID
        except Exception:
            response_data[interaction_id] = {"error": "Invalid ObjectId format"}

    if not object_ids:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail="No valid interaction_ids provided",
        )

    # Fetch child documents in a single query for efficiency
    interaction_cursor = db.interactions.find({"_id": {"$in": object_ids}})
    async for interaction in interaction_cursor:

        interaction["_id"] = str(interaction["_id"])
        interaction["conversation_id"] = str(interaction["conversation_id"])
        print(interaction)
        # interaction["conversation_id"] = str(interaction["conversation_id"])
        # Convert ObjectId to string
        response_data[id_mapping[interaction["_id"]]] = InteractionDetails(
            id=interaction["_id"], **interaction
        ).dict()

    # Fill missing child_ids with "not found" error
    for interaction_id in InteractionIds:
        if interaction_id not in response_data:
            response_data[interaction_id] = {"error": "Child not found"}
    return response_data

async def fetch_conversation_data(request,db):
    interaction_id=request.interaction_id
    # Find child document to get parentId
    interaction = await db.interactions.find_one(
        {"_id": ObjectId(interaction_id)}, {"conversation_id": 1}
    )
    if not interaction:
        raise HTTPException(status_code=404, detail="interaction not found")

    conversation_id = interaction["conversation_id"]

    # Find parent document

    conversation_details = await db.conversations.find_one({"_id": conversation_id})

    if not conversation_details:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation_details["_id"] = str(conversation_details["_id"])

    print("ConversationDetails",conversation_details["conversation_id"])
    file_name=CHAT_FILENAME_INITIAL+conversation_details["conversation_id"]+CHAT_DATA_EXTENSION

    file_path= os.path.join(CHAT_DATA_STORAGE_PATH,file_name)
    # file_path= CHAT_DATA_STORAGE_PATH + "\\" + conversation_details["conversation_id"] +CHAT_DATA_EXTENSION
    print(file_path)
    # "E:\isyenergy\mongodb\sessions_json\Session_Session_9901.json"
    try:
        with open(file_path, 'r') as f:  # 'r' for reading
            file_content = json.load(f) 
            
        print(file_content["interactions"])

        conversation_details["file_content"]=file_content["interactions"]

        return conversation_details
          
             # json.load() parses the JSON

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"File not found: {e}",
        )
    
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"JSON File not readable: {e}",
        )
    except Exception as e: # Catch other potential errors
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"JSON File not readable: {e}",
        )
    
    