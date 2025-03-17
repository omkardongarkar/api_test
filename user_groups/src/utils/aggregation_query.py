from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["Chatsee"]


def get_all_users_and_interaction_count(agent_id):
    pipeline = [
        {"$match": {"agent_id": ObjectId(agent_id)}},  # Filter by t_id
        {
            "$group": {
                "_id": None,
                "total_interaction_count": {"$sum": 1},  # Count total docs
                "unique_users": {"$addToSet": "$user_id"},  # Collect unique customers
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_interaction_count": 1,
                "total_unique_users": {
                    "$size": "$unique_users"
                },  # Count unique customers
            }
        },
    ]
    return pipeline
    # result = list(collection.aggregate(pipeline))
    # print(result)
    # return result[0] if result else {"total_interaction_count": 0, "total_unique_users": 0}


def get_conversation_query(pipeline):
    pipeline.extend(
        [
            {
                "$lookup": {
                    "from": "conversations",
                    "localField": "conversation_id",
                    "foreignField": "_id",
                    "as": "conversation_info",
                }
            },
            {"$unwind": "$conversation_info"},
        ]
    )
    return pipeline


def create_grouping_in_query(pipeline):

    pipeline.extend(
        [
            {
                "$group": {
                    "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour"}},
                    "unique_users_count": {"$addToSet": "$user_id"},
                    "unique_conversation_ids": {"$addToSet": "$conversation_id"},
                    "interaction_ids": {"$addToSet": "$_id"},
                    "all_users_count": {"$sum": 1},
                    "is_boolean_true_count": {
                        "$sum": {
                            "$cond": {
                                "if": {"$eq": ["$error_value", 1]},
                                "then": 1,
                                "else": 0,
                            }
                        }
                    },
                }
            },
        ]
    )
    return pipeline


def apply_internal_projection(pipeline):
    pipeline.extend(
        [
            {
                "$project": {
                    "_id": "$_id",
                    "unique_users_counts": {"$size": "$unique_users_count"},
                    "all_users_count": 1,
                    "unique_conversation_count": {"$size": "$unique_conversation_ids"},
                    "conversation_ids": ["$interaction_ids_ro"],
                    "total_interactions": {"$size": "$interaction_ids"},
                    "is_boolean_true_count": 1,
                    "user_ids": {
                        "$map": {
                            "input": "$unique_users_count",
                            "as": "user",
                            "in": {"$toString": "$$user"},
                        }
                    },
                    "conversation_ids": {
                        "$map": {
                            "input": "$unique_conversation_ids",
                            "as": "conversation",
                            "in": {"$toString": "$$conversation"},
                        }
                    },
                    "interaction_ids": {
                        "$map": {
                            "input": "$interaction_ids",
                            "as": "interaction",
                            "in": {"$toString": "$$interaction"},
                        }
                    },
                }
            },
        ]
    )
    return pipeline


def create_external_project(pipeline):
    pipeline.extend(
        [
            {
                "$group": {
                    "_id": None,
                    "overall_interactions": {"$sum": "$total_interactions"},
                    "overall_users": {"$sum": "$unique_users_counts"},
                    "data": {"$push": "$$ROOT"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "overall_interactions": 1,
                    "overall_users": 1,
                    "data": 1,
                }
            },
        ]
    )
    return pipeline


def get_match_filters(id, interaction_filter, conversation_filter):
    match_filter = {
        "$match": {
            "agent_id": ObjectId(id),
            **interaction_filter,
            **conversation_filter,
        }
    }

    return match_filter


def apply_match_filters(pipeline, match_filter):
    pipeline.extend([match_filter])
    return pipeline


def get_conversation_fields_post(
    geography,
    resolution,
    engagement_level,
    dominant_topic,
    avg_sentiment,
    drop_off_sentiments,
):
    conversation_filter_field = {}

    if geography:

        conversation_filter_field["conversation_info.geography"] = {"$in": geography}
    if resolution:
        conversation_filter_field["conversation_info.resolution"] = {"$in": resolution}
    if engagement_level:
        conversation_filter_field["conversation_info.engagement_level"] = {
            "$in": engagement_level
        }
    if dominant_topic:
        conversation_filter_field["conversation_info.dominant_topic"] = {
            "$in": dominant_topic
        }
    if avg_sentiment:
        conversation_filter_field["conversation_info.avg_sentiment"] = {
            "$in": avg_sentiment
        }
    if drop_off_sentiments:
        conversation_filter_field["conversation_info.drop_off_sentiments"] = {
            "$in": drop_off_sentiments
        }

    filter_fields = {
        "conversation_info.geography": geography,
        "conversation_info.resolution": resolution,
        "conversation_info.engagement_level": engagement_level,
        "conversation_info.dominant_topic": dominant_topic,
        "conversation_info.avg_sentiment": avg_sentiment,
        "conversation_info.drop_off_sentiments": drop_off_sentiments,
    }
    return conversation_filter_field


def get_interaction_filter_query(
    topic, sentiment, emotion, issue, query, risky_behaviour, intent
):
    # print("sentiment",sentiment)
    interaction_filter_fields = {}
    if topic:
        interaction_filter_fields["topic"] = {"$in": topic}
    if sentiment:
        interaction_filter_fields["sentiment"] = {"$in": sentiment}
    if emotion:
        interaction_filter_fields["emotion"] = {"$in": emotion}
    if issue:
        interaction_filter_fields["issue"] = {"$in": issue}
    if query:
        interaction_filter_fields["query"] = {"$in": query}
    if risky_behaviour:
        interaction_filter_fields["risky_behaviour"] = {"$in": risky_behaviour}
    if intent:
        interaction_filter_fields["intent"] = {"$in": intent}

    # print(interaction_filter_fields)
    return interaction_filter_fields



def create_materialised_view(pipeline):

    pipeline.extend([
        {
        "$out": "materialized_stadium_stats_check" 
    }

    ])
    
agent_id = "67b6d256f1239fa69e963e80"
geography = ["Dallas", "Philadelphia"]
resolution = []
engagement_level = []
dominant_topic = []
avg_sentiment = []
drop_off_sentiments = []

topic = []
sentiment = ["Positive"]
emotion = []
issue = []
query = []
risky_behaviour = []
intent = []


async def main():

    

    pipeline = []

    pipeline = get_conversation_query(pipeline)

    interaction_filter = get_interaction_filter_query(
        topic, sentiment, emotion, issue, query, risky_behaviour, intent
    )
    conversation_filter = get_conversation_fields_post(
        geography,
        resolution,
        engagement_level,
        dominant_topic,
        avg_sentiment,
        drop_off_sentiments,
    )

    all_filters = get_match_filters(agent_id, interaction_filter, conversation_filter)

    pipeline = apply_match_filters(pipeline, all_filters)

    pipeline = create_grouping_in_query(pipeline)
    pipeline = apply_internal_projection(pipeline)
    pipeline = create_external_project(pipeline)
    # pipeline = create_materialised_view(pipeline)
   

    records =await db["interactions"].aggregate(pipeline).to_list()
    print(records)

   

    # all_user_pipeline = get_all_users_and_interaction_count(agent_id)
    # interaction_user_count =await db["interactions"].aggregate(all_user_pipeline).to_list(None)
       
    

    # today = datetime.today()
    # thirty_days_ago = today - timedelta(days=70)

    # all_interaction_ids = []
    # all_user_ids = []
    

    # all_users_count, unique_users_counts, total_interactions = (
    #     sum(
    #         record.get(field)
    #         for record in records[0]["data"]
    #         if record.get("_id") >= thirty_days_ago
    #     )
    #     for field in ["all_users_count", "unique_users_counts", "total_interactions"]
    # )
    # result = {}
    # for record in records[0]["data"]:
    #     if record.get("_id") >= thirty_days_ago:
    #         all_interaction_ids.extend(record.get("interaction_ids"))
    #         all_user_ids.extend(record.get("user_ids"))

    # no_of_unique_users = len(set(all_user_ids))

    # result.update({"associated_interaction_ids": all_interaction_ids})
    # result.update({"number_of_users": len(all_user_ids)})
    # result.update({"users_percentage": (len(all_user_ids) / interaction_user_count[0].get("total_unique_users") * 100)})
    # result.update({"number_of_interactions": total_interactions})
    # result.update({"interaction_percentages": (total_interactions / interaction_user_count[0].get("total_interaction_count") * 100)})
    

    # retention = ((len(all_user_ids) - no_of_unique_users) / no_of_unique_users) * 100

    # result.update({"retention": retention})
    # print("result :", result)


# Filter records within the last 30 days
# filtered_data = [record for record in records[0]["data"] if record.get("_id") >= thirty_days_ago]
# print(filtered_data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
