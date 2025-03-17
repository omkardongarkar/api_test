from fastapi import HTTPException
from app_logging.logger import logger
from common.constants import StatusCode

# from ..database import get_db


def primary_filter_condition(combined_match_criteria, aggregrate_pipeline):
    logger.info(f"Building a match query string for filtering data started")
    aggregrate_pipeline.extend([{"$match": combined_match_criteria}])
    logger.info(f"Building a match query string for filtering data completed")
    return aggregrate_pipeline


def get_interaction_filter_query(
    topic, sentiment, emotion, issue, query, risky_behaviour, intent
):
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

    if (
        topic or sentiment or emotion or issue or query or risky_behaviour or intent
    ):  # Add $and only if we have at least one filter
        combined_match_criteria = {"$and": []}

        if "topic" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"topic": interaction_filter_fields["topic"]}
            )
        if "sentiment" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"sentiment": interaction_filter_fields["sentiment"]}
            )
            print("combined_match_criteria")
        if "emotion" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"emotion": interaction_filter_fields["emotion"]}
            )
        if "issue" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"issue": interaction_filter_fields["issue"]}
            )
        if "query" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"query": interaction_filter_fields["query"]}
            )
        if "risky_behaviour" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"risky_behaviour": interaction_filter_fields["risky_behaviour"]}
            )
        if "intent" in interaction_filter_fields:
            combined_match_criteria["$and"].append(
                {"intent": interaction_filter_fields["intent"]}
            )

    else:
        combined_match_criteria = {}
    has_interaction_filters = any(
        value is not None for value in combined_match_criteria.values()
    )
    return combined_match_criteria, has_interaction_filters


def primary_filter_aggeregation(aggregrate_pipeline, category):
    logger.info(f"Creating a query string for Grouping by {category} for  analytics ")
    aggregrate_pipeline.extend(
        [
            {
                "$group": {
                    "_id": f"${category}",
                    "unique_users_count": {"$addToSet": "$user_id"},
                    "unique_conversation_ids": {"$addToSet": "$conversation_id"},
                    "unique_interaction_ids": {"$addToSet": "$interaction_id"},
                    "interaction_ids": {"$addToSet": "$_id"},
                    "all_users_count": {"$sum": 1},
                    "is_boolean_true_count": {  # Count of is_boolean = true
                        "$sum": {
                            "$cond": {
                                "if": {
                                    "$eq": ["$error_value", 1]
                                },  # Corrected: Use boolean True
                                "then": 1,
                                "else": 0,
                            }
                        }
                    },
                }
            },
            
            {
                "$project": {
                    "category": "$_id",
                    "_id": 0,
                    "unique_users_count": {"$size": "$unique_users_count"},
                    "all_users_count": 1,
                    "unique_conversation_count": {"$size": "$unique_conversation_ids"},
                    "unique_interaction_Count": {"$size": "$unique_interaction_ids"},
                    "conversation_ids": ["$interaction_ids_ro"],
                    "total_interactions": {"$size": "$interaction_ids"},
                    "is_boolean_true_count": 1,
                    "user_ids": {  # Convert ObjectId to String
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
            
            {
                "$group": {
                "_id": None,
                "overall_interactions": { "$sum": "$unique_interaction_Count" },
                "overall_users": { "$sum": "$unique_users_count" },
                "data": { "$push": "$$ROOT" } 
                }
            },
            {
                "$project": {
                "_id": 0,
                "overall_interactions": 1,
                "overall_users": 1,
                "data": 1 
                }
            }
        ]
    )

    logger.info(f"Completed a query string for Grouping by {category} for  analytics ")
    return aggregrate_pipeline


def get_conversation_fields(
    geography,
    resolution,
    engagement_level,
    dominant_topic,
    avg_sentiment,
    drop_off_sentiments,
):
    conversation_filter_field = {}

    if geography:
        conversation_filter_field["conversation_info.geography"] = geography
    if resolution:
        conversation_filter_field["conversation_info.resolution"] = resolution
    if engagement_level:
        conversation_filter_field["conversation_info.engagement_level"] = (
            engagement_level
        )
    if dominant_topic:
        conversation_filter_field["conversation_info.dominant_topic"] = dominant_topic
    if avg_sentiment:
        conversation_filter_field["conversation_info.avg_sentiment"] = avg_sentiment
    if drop_off_sentiments:
        conversation_filter_field["conversation_info.drop_off_sentiments"] = (
            drop_off_sentiments
        )

    filter_fields = {
        "conversation_info.geography": geography,
        "conversation_info.resolution": resolution,
        "conversation_info.engagement_level": engagement_level,
        "conversation_info.dominant_topic": dominant_topic,
        "conversation_info.avg_sentiment": avg_sentiment,
        "conversation_info.drop_off_sentiments": drop_off_sentiments,
    }
    return filter_fields


def add_conversation_field(filter_fields, match_criteria):
    for field_name, field_value in filter_fields.items():
        if field_value is not None:
            has_conversation_filters = True
            if isinstance(field_value, list):
                match_criteria["$and"].append({field_name: {"$in": field_value}})
            elif isinstance(field_value, str):
                match_criteria[field_name] = {"$regex": field_value, "$options": "i"}
            else:
                match_criteria[field_name] = field_value

    return match_criteria, has_conversation_filters


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


def group_by_date_query(pipeline, group_by):
    pipeline.extend(
        [  # These stages are always required, so no conditional check is required
            {
                "$project": {
                    "date": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                    },
                    "category": f"${group_by}",
                }
            },
            {
                "$group": {
                    "_id": {"date": "$date", "category": "$category"},
                    "interaction_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.date": -1}},
        ]
    )
    return pipeline


async def get_data_from_db(db, agg_pipeline):
    """
    This method is used to get data from database based on query definded in agg_pipeline
    """
    try:
        results = await db.interactions.aggregate(agg_pipeline).to_list(None)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=StatusCode.BAD_REQUEST,
            detail=f"No valid interaction_ids provided: {e}",
        )


async def organise_data_datewise(results):
    daywise_data = {}
    for entry in results:
        date = entry["_id"]["date"]
        sentiment = entry["_id"]["category"]
        count = entry["interaction_count"]

        if date not in daywise_data:
            daywise_data[date] = []

        daywise_data[date].append({"category": sentiment, "count": count})

    return daywise_data


async def extract_retention_percentage(results):
    overall_interactions = results[0]["overall_interactions"]
    overall_users = results[0]["overall_users"]
    print(overall_interactions)
    result_data=results[0]["data"]
    for result in result_data:
        # user_percentage = res
        error_rate = (result["is_boolean_true_count"]/result["unique_interaction_Count"])*100
        user_percentage=(result["unique_users_count"]/overall_users)*100
        interaction_percentage=(result["unique_interaction_Count"]/overall_interactions)*100
        retention=(result["unique_conversation_count"]-result["unique_users_count"])/result["unique_users_count"]*100
        result.update({"retention_in_percentage":retention})
        result.update({"error_rate":error_rate})
        result.update({"interaction_percentage":interaction_percentage})
        result.update({"user_percentage":user_percentage})

    return result_data


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
        print(geography)
        conversation_filter_field["conversation_info.geography"] = geography
    if resolution:
        conversation_filter_field["conversation_info.resolution"] = resolution
    if engagement_level:
        conversation_filter_field["conversation_info.engagement_level"] = (
            engagement_level
        )
    if dominant_topic:
        conversation_filter_field["conversation_info.dominant_topic"] = dominant_topic
    if avg_sentiment:
        conversation_filter_field["conversation_info.avg_sentiment"] = avg_sentiment
    if drop_off_sentiments:
        conversation_filter_field["conversation_info.drop_off_sentiments"] = (
            drop_off_sentiments
        )

    filter_fields = {
        "conversation_info.geography": geography,
        "conversation_info.resolution": resolution,
        "conversation_info.engagement_level": engagement_level,
        "conversation_info.dominant_topic": dominant_topic,
        "conversation_info.avg_sentiment": avg_sentiment,
        "conversation_info.drop_off_sentiments": drop_off_sentiments,
    }
    return conversation_filter_field
