# app/core/dependencies.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import settings

def get_embedding():
    return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

def get_vector_store():
    embeddings = get_embedding()
    return Chroma(
        persist_directory=settings.VECTOR_DB_PATH,
        embedding_function=embeddings
    )
