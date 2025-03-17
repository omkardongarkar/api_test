from datetime import datetime, timedelta

from bson import ObjectId

from cross_agents_performance.schemas.users_schemas import RequestUsers




# query_pipeline=[
  
    # {
    #     "$match": {
            
	# 	    "geography":"Dallas",
						
            
    #     }
    # },
#     {
#         "$lookup": {
#             "from": "agents",      
#             "localField": "agent_id",  
#             "foreignField": "_id", 
#             "as": "agents_info"
#         }
#     },
#     {
#         "$unwind": "$agents_info"
#     },
# 	{
#         "$lookup": {
#             "from": "interactions",    
#             "localField": "_id",      
#             "foreignField": "conversation_id",  
#             "as": "interaction_info"
#         }
#     },
    
#     {
#         "$match": {
# 		"interaction_info.sentiment": {"$in": ["Negative"] 
#             }
# 		}
# 	},
# 	{
#         "$group": {
#             "_id": {
#                 "agent_id": "$agent_id",
#                 "agent_name": "$agents_info.agent_name"
#             },
#             "completed_count": {
#                 "$sum": { "$cond": [{ "$eq": ["$resolution", "Satisfied"] }, 1, 0] }
#             },
#             "total_count": { "$sum": 1 } 
#         }
#     },
 
# ]

def calculate_rating(check_count, total, scale=5):
    return round((check_count / total) * scale, 2) if total else 0

def create_conversation_filter(basic_filters, request: RequestUsers):
    if request.agent_ids:
        basic_filters["agent_id"] = {
            "$in": [ObjectId(sid) for sid in request.agent_ids]
        }

    if request.geography:
        basic_filters["geography"] = {"$in": request.geography}

    if request.resolution:
        basic_filters["resolution"] = {"$in": request.resolution}

    return basic_filters


def create_interaction_filter(interaction_filters, request: RequestUsers):

    if request.sentiment:
        interaction_filters["interaction_info.sentiment"]= {"$in": request.sentiment}
    
    if request.emotion:
        interaction_filters["interaction_info.emotion"]= {"$in": request.emotion}
    return interaction_filters

def create_interactions_lookup(query_issue_pipeline):
    query_issue_pipeline.extend([{
			"$lookup": {
				"from": "interactions",
				"localField": "_id",
				"foreignField": "conversation_id",
				"as": "interaction_info"
			}
		},
		])
    
    return query_issue_pipeline



def create_agent_lookup(query_issue_pipiline):
    query_issue_pipiline.extend([
        {
        "$lookup": {
            "from": "agents",      
            "localField": "agent_id",  
            "foreignField": "_id", 
            "as": "agents_info"
        }
    },
    {
        "$unwind": "$agents_info"
    },
    ])
    return query_issue_pipiline


def resolution_count_query(query_issue_pipiline):
    query_issue_pipiline.extend([
        {
        "$group": {
            "_id": {
                "agent_name": "$agents_info.agent_name"
            },
            "resolution_count": {
                "$sum": { "$cond": [{ "$eq": ["$resolution", "Satisfied"] }, 1, 0] }
            },
            "total_count": { "$sum": 1 } 
        }
    },


    ])
    return query_issue_pipiline

def apply_conversation_filter(query_issue_pipeline, basic_filters):
    if basic_filters:
        query_issue_pipeline.extend([{"$match": basic_filters}])
    return query_issue_pipeline

def apply_interaction_filter(query_issue_pipeline, interaction_filters):
    
    query_issue_pipeline.extend(
        [
            {"$match":  interaction_filters} ,
        ]
    )
    print("interaction_filters",interaction_filters)
    return query_issue_pipeline






    








    