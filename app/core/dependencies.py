# app/core/dependencies.py
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.core.config import settings

def get_embedding():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def create_vector_store(chunks: List[Document]) -> Chroma:
    embeddings = get_embedding()
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.VECTOR_DB_PATH,
        collection_name=settings.VECTOR_DB_COLLECTION_NAME
    )
