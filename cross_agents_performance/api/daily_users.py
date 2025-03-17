from collections import defaultdict
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

from cross_agents_performance.schemas.users_schemas import RequestUsers
from cross_agents_performance.views.agents_users import apply_conversation_filter, apply_interaction_filter, conversations_lookup_unwind, create_conversation_filter, create_grouping_result, create_interaction_filter, interaction_lookup

async def count_users_daily(request:RequestUsers,db):

    query_pipeline = []
    

    interaction_filters = []
    
    if request.days:
        date_filter = datetime.utcnow() - timedelta(days=request.days)


    if request.days:
        basic_filters = {"timestamp": {"$gte": date_filter}}
    else:
        basic_filters={}

  

    interaction_filters= create_interaction_filter(interaction_filters,request)
    basic_filters = create_conversation_filter(basic_filters,request)
    query_pipeline = apply_conversation_filter(query_pipeline, basic_filters)


    query_pipeline = conversations_lookup_unwind(query_pipeline)


    query_pipeline = interaction_lookup(query_pipeline)

    query_pipeline = apply_interaction_filter(query_pipeline, interaction_filters)


    query_pipeline = create_grouping_result(query_pipeline)



    results = await  db.conversations.aggregate(query_pipeline).to_list(None)

    agentwise_data = defaultdict(lambda: {"dates": [], "total_users_count": 0})
    for result in results:
        agent_name = result["_id"]["agent_name"]
        date = result["_id"]["date"].isoformat()
        audience_count = result["users_count"]
        agentwise_data[agent_name]["dates"].append({"date": date, "users_count": audience_count})
        agentwise_data[agent_name]["total_users_count"] += audience_count

    # Print the structured output
    # print(dict(agentwise_data))



    return agentwise_data
    
    # Print the results
    # for result in results:
    #     print(result)

