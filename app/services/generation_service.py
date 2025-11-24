from google import genai
from langchain_core.documents import Document
from typing import List, Tuple
from app.core.config import settings
from app.services.rag_service import retrieve_and_rerank


class GenerationService:
    def __init__(self):
        # Initialize the client once
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def build_prompt(self, context: str, query: str) -> str:
        """Build prompt using the template stored in settings."""
        return settings.SYSTEM_PROMPT.format(context=context, query=query)

    def generate_answer(self, query: str, vectore_store):
        # Get retrieved and reranked documents
        retrieved_and_reranked_doc = retrieve_and_rerank(query=query, vectore_store=vectore_store)
        
        # Fix: access the function result correctly (it was trying to index the function itself)
        top = retrieved_and_reranked_doc[0]  # Get the first document
        
        # Extract content and metadata
        if isinstance(top, tuple):
            top_passage = top[1].page_content
            top_page = top[1].metadata.get("page_number", None)
        else:
            top_passage = top.page_content
            top_page = top.metadata.get("page_number", None)
        
        # Build prompt
        prompt = self.build_prompt(top_passage, query)
        
        # Generate content using the new API
        response = self.client.models.generate_content(
            model=settings.LLM_NAME,  # e.g., "gemini-2.0-flash-exp" or "gemini-2.5-flash"
            contents=prompt
        )
        
        return {
            "answer": response.text,
            "sources": top_page
        }