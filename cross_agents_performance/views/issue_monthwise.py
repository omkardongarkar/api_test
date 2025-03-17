from datetime import datetime, timedelta
import json
from bson import ObjectId
from pymongo import MongoClient
from collections import defaultdict
import time



from cross_agents_performance.schemas.users_schemas import RequestUsers

# Connect to MongoDB

def count_resolution_rate(data):
    # print("data",data)
    for entry in data:
        completions = entry["query"]["resolution"]
        total_count = entry["count"]
        satisfied_count = completions.count("Satisfied")
        resolution_rate = (satisfied_count / total_count) * 100 if total_count > 0 else 0
        entry["resolution_rate"] = resolution_rate
        # entry["query"]=entry["query"]["query"]
        
        entry["query_name"]=entry["query"]["query"]
        del entry["query"]
    return data

def create_conversation_filter(basic_filters, request: RequestUsers):
    

    if request.geography:
        basic_filters["conversations_info.geography"] = {"$in": request.geography}

    if request.resolution:
        basic_filters["conversations_info.resolution"] = {"$in": request.resolution}

    return basic_filters



def create_conversation_lookup(query_issue_pipeline):
    query_issue_pipeline.extend([{
			"$lookup": {
				"from": "conversations",
				"localField": "conversation_id",
				"foreignField": "_id",
				"as": "conversations_info"
			}
		},
		{ "$unwind": "$conversations_info" },])
    
    return query_issue_pipeline

def apply_conversation_filter(query_issue_pipeline, basic_filters):
    if basic_filters:
        query_issue_pipeline.extend([{"$match": basic_filters}])
    return query_issue_pipeline




def create_interaction_filter(interaction_filters, request: RequestUsers):

    if request.agent_ids:
        interaction_filters["agent_id"] = {
            "$in": [ObjectId(sid) for sid in request.agent_ids]
        }
    

    if request.sentiment:
        interaction_filters["sentiment"]= {"$in": request.sentiment}
    
    if request.emotion:
        interaction_filters.append(
            {"emotion": {"$in": request.emotion}}
        )
    return interaction_filters


def apply_interaction_filter(query_issue_pipeline, interaction_filters):
    
    query_issue_pipeline.extend(
        [
            {"$match":  interaction_filters} ,
        ]
    )
    print("interaction_filters",interaction_filters)
    return query_issue_pipeline


def create_agent_lookup(query_issue_pipiline):
    query_issue_pipiline.extend([
        {
			"$lookup": {
				"from": "agents",  
				"localField": "agent_id",  
				"foreignField": "_id",  
				"as": "agent_info"
			}
		},
		{
			"$unwind": "$agent_info"  
		},
    ])
    return query_issue_pipiline



def create_issues_count_monthwise(query_issue_pipeline):
    query_issue_pipeline.extend([
    {
                "$group": {
                    "_id": {
                        "agent_name": "$agent_info.agent_name",  
                        "month": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}},
                        
                        
                    },
                    
                    "count": { "$sum": 1 }  
                }
            },
        { "$sort": {"_id.month": 1 } }

    ])
    return query_issue_pipeline

def create_group_by_query_and_count(query_issue_pipeline):
        query_issue_pipeline.extend([
            {
        "$group": {
            "_id": {
                "agent_id": "$agent_id",
                "agent_name": "$agent_info.agent_name",
                "query": "$query",
            },
            "count": { "$sum": 1 },
            "issue": { "$sum": { "$cond": [{ "$eq": ["$issue", 1] }, 1, 0] } },
            "resolution_fields": { "$push": "$conversations_info.resolution" } 
            }
        },
        ])

        return query_issue_pipeline


def group_agentswise_queries(query_issue_pipeline):
    query_issue_pipeline.extend([
            { "$sort": { "_id.agent_id": 1, "count": -1 } },

    {
        "$group": {
            "_id": {
                "agent_id": "$_id.agent_id",
                "agent_name": "$_id.agent_name",
                
            },
            "top_queries": {
                "$push": {
                    "query": "$_id.query",
                    "count": "$count",
                    "issue": "$issue",
                    "resolution": "$resolution_fields" 
                }
            }
        }
    },
        ])

    return query_issue_pipeline   



pipeline = [
		
		{
			"$lookup": {
				"from": "conversations",
				"localField": "conversation_id",
				"foreignField": "_id",
				"as": "conversations_info"
			}
		},
		{ "$unwind": "$conversations_info" },
		
		{
			"$match": {
				"conversations_info.resolution": { "$in": ["Satisfied", "Dropped", "Unsatisfied"] },
				"conversations_info.geography": { "$in": ["Dallas", "San Antonio","San Diego","Philadelphia","Houston"] }
			}
		},	
		
		{
			"$match": {
				"issue": 1,  
				}
		},
		{
			"$lookup": {
				"from": "agents",  
				"localField": "agent_id",  
				"foreignField": "_id",  
				"as": "agent_info"
			}
		},
		{
			"$unwind": "$agent_info"  
		},
		{
			"$group": {
				"_id": {
					"agents_name": "$agent_info.agent_name",  
					"month": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}},
					
					
				},
				
				"count": { "$sum": 1 }  
			}
		},
	   { "$sort": {"_id.month": 1 } }
	]


async def get_issues_monthly_count(request:RequestUsers,db):
    query_issue_pipeline = []
    

    interaction_filters = []
    interaction_filters={"issue":1}
    
    if request.days:
        date_filter = datetime.utcnow() - timedelta(days=request.days)


    if request.days:
        interaction_filters = {"timestamp": {"$gte": date_filter}}
    else:
        interaction_filters={}

    conversation_filter ={}

    conversation_filter = create_conversation_filter(conversation_filter,request)

    query_issue_pipeline = create_conversation_lookup(query_issue_pipeline)

    query_issue_pipeline = apply_conversation_filter(query_issue_pipeline,conversation_filter)

    interaction_filter = create_interaction_filter(interaction_filters,request)

    query_issue_pipeline =apply_interaction_filter(query_issue_pipeline,interaction_filter)

    query_issue_pipeline = create_agent_lookup(query_issue_pipeline)


    query_issue_pipeline = create_issues_count_monthwise(query_issue_pipeline)













    results = await  db.interactions.aggregate(query_issue_pipeline).to_list(None)
    # print(results)

    sessionwise_data = defaultdict(lambda: {"months": [], "total_session_count": 0})
    for result in results:
        print(result)
        agent_name = result["_id"]["agent_name"]
        month = result["_id"]["month"]
        audience_count = result["count"]
        sessionwise_data[agent_name]["months"].append({"month": month, "session_count": audience_count})
        sessionwise_data[agent_name]["total_session_count"] += audience_count

    
    print(dict(sessionwise_data))



    return sessionwise_data



async def get_top_issue_query_resolution(request:RequestUsers,db):
    query_issue_pipeline = []
    

    interaction_filters = []
    
    if request.days:
        date_filter = datetime.utcnow() - timedelta(days=request.days)


    if request.days:
        interaction_filters = {"timestamp": {"$gte": date_filter}}
    else:
        interaction_filters={}
    # interaction_filters["issue"]=1

    conversation_filter ={}

    conversation_filter = create_conversation_filter(conversation_filter,request)
     

    query_issue_pipeline = create_conversation_lookup(query_issue_pipeline)
    
    query_issue_pipeline = apply_conversation_filter(query_issue_pipeline,conversation_filter)
    

    interaction_filter = create_interaction_filter(interaction_filters,request)
    


    

    query_issue_pipeline =apply_interaction_filter(query_issue_pipeline,interaction_filter)
    

    query_issue_pipeline = create_agent_lookup(query_issue_pipeline)

    query_issue_pipeline= create_group_by_query_and_count(query_issue_pipeline)

    query_issue_pipeline = group_agentswise_queries(query_issue_pipeline)
    print(query_issue_pipeline)

    data = await  db.interactions.aggregate(query_issue_pipeline).to_list(None)
    print("data pipeline",query_issue_pipeline ) 

    et1=time.time()
    
    # print(data)


    agent_data = defaultdict(lambda: {"agent_name": "", "all_queries": [], "filtered_queries": []})

    # To store overall counts across all sports
    overall_queries = []
    overall_filtered_queries = []

    for record in data:
        agent_id = record["_id"]["agent_id"]
        agent_name = record["_id"]["agent_name"]
        top_queries = record["top_queries"]
        

        agent_data[agent_id]["agent_name"] = agent_name
        
        for query in top_queries:
            query_entry = {"query": query["query"], "count": query["count"], "agent_name": agent_name,"resolution":query["resolution"]}
            filtered_entry = {"query": query["query"], "count": query["issue"], "agent_name": agent_name,"resolution":query["resolution"]}
            
            # Add to total run-outs (per sport)
            agent_data[agent_id]["all_queries"].append(query_entry)
            
            # Add to total list (for all sports)
            overall_queries.append(query_entry)
            
            # Add to filtered run-outs (where issue = 1)
            if query["issue"] > 0:
                agent_data[agent_id]["filtered_queries"].append(filtered_entry)
                overall_filtered_queries.append(filtered_entry)

    # Extract top 5 run-outs for each sport
    final_results = []

    for agent_id, agent_info in agent_data.items():
        final_results.append({
            "agent_id":str(agent_id),
            "agent_name": agent_info["agent_name"],
            "top_queries_details": sorted(agent_info["all_queries"], key=lambda x: x["count"], reverse=True)[:5],
            "top_issues_details": sorted(agent_info["filtered_queries"], key=lambda x: x["count"], reverse=True)[:5]
            
        })
        
    print("final_results",final_results)

    



    # Extract top 25 run-outs across all sports (including sport names)
    top_25_queries_all = sorted(overall_queries, key=lambda x: x["count"], reverse=True)[:10]
    top_25_issues = sorted(overall_filtered_queries, key=lambda x: x["count"], reverse=True)[:10]

    

    

    
    def calculate_completion_rate(data):
        results = []
        for entry in data:
            sport_name = entry["agent_name"]
            run_name = entry["query"]
            total_count = entry["count"]
            satisfied_count = entry["resolution"].count("Satisfied")
            resolution_rate = (satisfied_count / total_count) *100 if total_count > 0 else 0
            
            results.append({
                "sport_name": sport_name,
                "run": run_name,
                "completion_rate": resolution_rate
            })
        return results



    # top_25_queries_all = count_resolution_rate(top_25_queries_all)   
    top_25_queries_all = calculate_completion_rate(top_25_queries_all)   
    # # print("top_25_queries_all",top_25_queries_all) 
    # top_25_issues = count_resolution_rate(top_25_issues)
    top_25_issues = calculate_completion_rate(top_25_issues)


    # Append overall top 25 results
    final_results.append({
        
        "all_top_queries_details": top_25_queries_all,
        "all_top_issues_details": top_25_issues
    })

    return final_results

    

        

    

