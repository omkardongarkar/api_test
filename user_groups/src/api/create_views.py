from fastapi import HTTPException
from common.constants import StatusCode
from user_groups.src.models.schemas import RequestFilterInteraction
from user_groups.src.utils.aggregation_query import *
from pymongo.errors import PyMongoError
def create_view_in_db(request: RequestFilterInteraction,db):
    
    
    pipeline = []

    pipeline = get_conversation_query(pipeline)

    interaction_filter = get_interaction_filter_query(
        request.topic, request.sentiment, request.emotion, request.issue, request.query, request.risky_behaviour, request.intent
    )
    conversation_filter = get_conversation_fields_post(
        request.geography,
        request.resolution,
        request.engagement_level,
        request.dominant_topic,
        request.avg_sentiment,
        request.drop_off_sentiments,
    )

    all_filters = get_match_filters(request.agent_id, interaction_filter, conversation_filter)

    pipeline = apply_match_filters(pipeline, all_filters)

    pipeline = create_grouping_in_query(pipeline)
    pipeline = apply_internal_projection(pipeline)
    pipeline = create_external_project(pipeline)
    # pipeline = create_materialised_view(pipeline)
    return pipeline
