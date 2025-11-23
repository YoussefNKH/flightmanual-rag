# app/core/config.py
import os 
from dotenv import load_dotenv

load_dotenv()

#this class for all environment variables needed to run the server

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    VECTOR_DB_PATH = "vector_store/chroma_db"
    DATA_PATH = "data/documents/"
settings = Settings()