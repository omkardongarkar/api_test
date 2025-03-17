from datetime import datetime, timedelta
from common.database import get_db,conversations_collection
from cross_agents_performance.views.resolution_rate_views import apply_conversation_filter, apply_interaction_filter, calculate_rating, create_agent_lookup, create_conversation_filter, create_interaction_filter, create_interactions_lookup, resolution_count_query


async def all_agents_resolution_rate(request,db):
    query_issue_pipeline = []
    

    conversation_filter = []
    
    if request.days:
        date_filter = datetime.utcnow() - timedelta(days=request.days)


    if request.days:
        conversation_filter = {"timestamp": {"$gte": date_filter}}
    else:
        conversation_filter={}

    interaction_filters ={}


    conversation_filters = create_conversation_filter(conversation_filter,request)

    query_issue_pipeline = apply_conversation_filter(query_issue_pipeline, conversation_filters)

    query_issue_pipeline = create_agent_lookup(query_issue_pipeline)

    interaction_filters = create_interaction_filter(interaction_filters,request)

    query_issue_pipeline=create_interactions_lookup(query_issue_pipeline)

    query_issue_pipeline = apply_interaction_filter(query_issue_pipeline,interaction_filters)
    
    query_issue_pipeline =  resolution_count_query (query_issue_pipeline)

    print("query_issue_pipeline",query_issue_pipeline)


    data =await conversations_collection.aggregate(query_issue_pipeline).to_list()

    

   

    result = []
    for item in data:
        agent_name = item["_id"]["agent_name"]
        rating = calculate_rating(item["resolution_count"], item["total_count"])
        result.append({"agent_name": agent_name, "resolution_rate": rating})

    


    return result