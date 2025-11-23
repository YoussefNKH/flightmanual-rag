# app/core/config.py
import os 
from dotenv import load_dotenv

load_dotenv()

#this class for all environment variables needed to run the server

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    VECTOR_DB_PATH = "vector_store/chroma_db"
    DATA_PATH = "data/documents/"
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150
    LLM_NAME = "gemini-2.5-flash"
    TOP_K = 3
    SYSTEM_PROMPT=""
settings = Settings()