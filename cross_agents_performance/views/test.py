from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # Update with your connection string
db = client["Chatsee"]  # Replace with your database name

audience_collection = db["conversations"]
days = None

if days:
    date_filter = datetime.utcnow() - timedelta(days=days)


agent_ids = ["67b6d256f1239fa69e963e80", "67b6d310f1239fa69e963e83"]
geography = ["Dallas", "San Antonio", "San Diego"]  # Example input, modify as needed
resolution = ["Unsatisfied", "Satisfied"]  # Example input, modify as needed
sentiment = ["Positive", "Neutral"]  # Example input, modify as needed
emotion = ["Regret", "ball2"]

if days:
    basic_filters = {"timestamp": {"$gte": date_filter}}
else:
    basic_filters={}


def create_conversation_filter(basic_filters):
    if agent_ids:
        basic_filters["agent_id"] = {"$in": [ObjectId(sid) for sid in agent_ids]}

    if geography:
        basic_filters["geography"] = {"$in": geography}

    if resolution:
        basic_filters["resolution"] = {"$in": resolution}

    return basic_filters


def apply_conversation_filter(query_pipeline, basic_filters):
    query_pipeline.extend([{"$match": basic_filters}])
    return query_pipeline


def create_interaction_filter(query_pipline, interaction_filters):
    query_pipeline.extend(
        [
            {"$match": {"$and": interaction_filters} if interaction_filters else {}},
        ]
    )
    return query_pipeline


def conversations_lookup_unwind(query_pipeline):
    query_pipeline.extend(
        [
            {
                "$lookup": {
                    "from": "agents",
                    "localField": "agent_id",
                    "foreignField": "_id",
                    "as": "users_info",
                }
            },
            {"$unwind": "$users_info"},
        ]
    )
    return query_pipeline


def interaction_lookup(query_pipeline):
    query_pipeline.extend(
        [
            {
                "$lookup": {
                    "from": "interactions",
                    "localField": "_id",
                    "foreignField": "conversation_id",
                    "as": "interaction_info",
                }
            },
        ]
    )
    return query_pipeline


def create_grouping_result(query_pipeline):
    query_pipeline.extend(
        [
            {
                "$group": {
                    "_id": {
                        "date": "$timestamp",
                        "agent_name": "$users_info.agent_name",
                    },
                    "users_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.date": 1}},
        ]
    )
    return query_pipeline


query_pipeline = []
# print(f"$match: {basic_filters}")

interaction_filters = []

if sentiment:
    interaction_filters.append({"interaction_info.sentiment": {"$in": sentiment}})
if emotion:
    interaction_filters.append({"interaction_info.emotion": {"$in": emotion}})


basic_filters = create_conversation_filter(basic_filters)
query_pipeline = apply_conversation_filter(query_pipeline, basic_filters)


query_pipeline = conversations_lookup_unwind(query_pipeline)


query_pipeline = interaction_lookup(query_pipeline)

query_pipeline = create_interaction_filter(query_pipeline, interaction_filters)


query_pipeline = create_grouping_result(query_pipeline)



results = audience_collection.aggregate(query_pipeline)

# Print the results
for result in results:
    print(result)
