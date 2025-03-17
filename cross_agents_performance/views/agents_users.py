from bson import ObjectId
from datetime import datetime, timedelta

from cross_agents_performance.schemas.users_schemas import RequestUsers


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


def apply_conversation_filter(query_pipeline, basic_filters):
    query_pipeline.extend([{"$match": basic_filters}])
    return query_pipeline


def apply_interaction_filter(query_pipline, interaction_filters):
    query_pipline.extend(
        [
            {"$match": {"$and": interaction_filters} if interaction_filters else {}},
        ]
    )
    return query_pipline


def create_interaction_filter(interaction_filters, request: RequestUsers):

    if request.sentiment:
        interaction_filters.append(
            {"interaction_info.sentiment": {"$in": request.sentiment}}
        )
    if request.emotion:
        interaction_filters.append(
            {"interaction_info.emotion": {"$in": request.emotion}}
        )


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


def session_monthwise(query_pipeline):
    query_pipeline.extend([

        {"$group": {
        "_id": {
            "month": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}},
            "agent_name": "$users_info.agent_name"
        },
        "session_count": {"$sum": 1}
    }},
    {"$sort": {"_id.month": 1}}

    ])
    return query_pipeline
