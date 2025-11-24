# app/api/endpoints.py
from fastapi import APIRouter, HTTPException
from app.models.pydantic_models import QueryRequest, QueryResponse


router = APIRouter()

#getting the global vector store and generation service
def get_vector_store():
    from app.main import vector_store
    if vector_store is None:
        raise HTTPException(
            status_code=503,
            detail="Vector store not initialized. Server is still starting up."
        )
    return vector_store


def get_generation_service():
    from app.main import generation_service
    if generation_service is None:
        raise HTTPException(
            status_code=503,
            detail="Generation service not initialized. Server is still starting up."
        )
    return generation_service


# Ask endpoint
@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    vector_store = get_vector_store()
    generation_service = get_generation_service()
    result = generation_service.generate_answer(request.query, vector_store)
    raw_pages =  result.get("sources")
    pages = [raw_pages]
    return QueryResponse(
    answer=result["answer"],
    pages=pages
)
