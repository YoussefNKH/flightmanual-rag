# app/services/rag_service.py
from sentence_transformers import CrossEncoder
from app.core.config import settings
# Initialize the reranker model from Haugging Face 
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def retrieve_and_rerank(query: str, vectore_store):
    # Retrieve initial documents
    results = vectore_store.similarity_search(query, k=settings.TOP_K)
    pairs = [(query, doc.page_content) for doc in results]
    scores = reranker.predict(pairs)
    scored_results = list(zip(results, scores))
    scored_results.sort(key=lambda x: x[1], reverse=True)

    # Return top_k documents after reranking
    
    top_results = [doc for doc, score in scored_results[:settings.TOP_K]]
    return top_results