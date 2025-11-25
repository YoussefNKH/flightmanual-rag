# app/core/config.py
import os 
from dotenv import load_dotenv

load_dotenv()

#this class for all environment variables needed to run the server and the paths and other settings

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    VECTOR_DB_PATH = "vector_store/chroma_db"
    VECTOR_DB_COLLECTION_NAME = "boeing_737_manual"
    DATA_PATH = "data/documents/"
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150
    LLM_NAME = "gemini-2.5-pro"
    TOP_K = 3
    SYSTEM_PROMPT="""
You are a Boeing 737 operations expert.

Use ONLY the context below to answer the question concisely.

Context:
{context}

Question:
{query}

Provide the answer and mention the page numbers if applicable.
"""
settings = Settings()