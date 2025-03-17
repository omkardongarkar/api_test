from fastapi import APIRouter, Depends
from business_query.src.api import business_query
from business_query.src.models import create_query_model

router = APIRouter()


@router.post("/create_query")
async def get_interactions(request: create_query_model.CreateQueryRequest):
    """Fetch conversation with  pagination, and date filtering"""
    query = request.query
    duration = request.duration

    return business_query.create_query(query, duration)
