# app/models/pydantic_models.py
# app/models/pydantic_models.py
from pydantic import BaseModel, Field


# The output format
class QueryResponse(BaseModel):
    answer: str
    pages: list[int]


# The input format
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The question to ask about the flight manual")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Looking at the panel scan responsibilities for when the aircraft is stationary, who is responsible for the forward aisle stand?"
            }
        }
