from collections import defaultdict
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

from cross_agents_performance.schemas.users_schemas import RequestUsers
from cross_agents_performance.views.agents_users import apply_conversation_filter, apply_interaction_filter, conversations_lookup_unwind, create_conversation_filter, create_grouping_result, create_interaction_filter, interaction_lookup, session_monthwise

async def get_sessions_monthly(request:RequestUsers,db):

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


    query_pipeline = session_monthwise(query_pipeline)



    results = await  db.conversations.aggregate(query_pipeline).to_list(None)
    print(results)

    sessionwise_data = defaultdict(lambda: {"months": [], "total_session_count": 0})
    for result in results:
        agent_name = result['_id']["agent_name"]
        month = result['_id']["month"]
        audience_count = result["session_count"]
        sessionwise_data[agent_name]["months"].append({"month": month, "session_count": audience_count})
        sessionwise_data[agent_name]["total_session_count"] += audience_count

    
    print(dict(sessionwise_data))



    return sessionwise_data
    
    # Print the results
    # for result in results:
    #     print(result)

