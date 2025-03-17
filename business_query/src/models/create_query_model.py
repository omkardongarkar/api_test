from typing import Optional
from pydantic import BaseModel, Field


class CreateQueryRequest(BaseModel):
    query: str = Field(..., description="The query string to execute.")
    duration: str = Field(
        ..., description="The duration for the query (e.g., '1h', '30m', '1d')."
    )
