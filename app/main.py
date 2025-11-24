# app/main.py
from fastapi.concurrency import asynccontextmanager
from app.api import endpoints
from app.core.dependencies import create_vector_store
from app.services.generation_service import GenerationService
from app.services.pipeline import PipelineService
from fastapi import FastAPI
from app.core.config import settings
from pathlib import Path
import uvicorn

# Global variables
vector_store = None
generation_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store, generation_service
    
    print(" Starting up... Processing document and creating vector store")
    
    # Initialize pipeline service to  initialize vector store and generation service
    pipeline_service = PipelineService()
    
    # Process document and create vector store before starting the server
    vector_store = pipeline_service.process_and_store(
        file_path="data/documents/Boeing B737 Manual.pdf",
        create_vector_store=create_vector_store
    )
    # Initialize generation service
    generation_service = pipeline_service.generation_service
    
    print(" Vector store and generation service initialized successfully")
    
    yield  
    
    print(" Shutting down...")

app = FastAPI(
    title="Flight Manual RAG API",
    description="Question Answering API for Boeing 737 Manual",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(endpoints.router)


def get_vector_store():
    return vector_store


def get_generation_service():
    return generation_service

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )