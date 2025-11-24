# 📚 RAG System with LangChain, ChromaDB, Gemini API & Cross-Encoder Re-ranking
A modular Retrieval-Augmented Generation pipeline using hybrid chunking, semantic metadata, and cross-encoder reranking for high-accuracy technical question answering.

---

## 🚀 Overview

This project implements a complete RAG (Retrieval-Augmented Generation) system built on:

- **LangChain** for orchestration  
- **ChromaDB** as the local vector store  
- **all-MiniLM-L6-v2** for text embeddings  
- **Cross-Encoder** for intelligent re-ranking of retrieved chunks  
- **Gemini API** for final answer generation  
- **Hybrid chunking strategy** (structural + semantic + adaptive)  
- **Metadata-rich context** for precise grounding 
- **FastApi** 

The system processes  documents  PDF transform them into meaningful chunks, indexes them, retrieves relevant chunks for a user query, re-ranks them with a cross-encoder, and generates grounded answers with source citations. 
---

## 🧱 Project Architecture
```
flightmanual-rag
├── .env.example                  # the envirement variable example
├── .gitignore
├── README.md
├── requirements.txt               
├── data
│    └── documents
│        └── Boeing B737 Manual.pdf
└── vector_store
│    └── chroma_db                 #vector_db
└── app
    ├── main.py
    ├── api
    │   └── endpoints.py           #the endpoint of the api
    ├── core
    │   ├── config.py              #contains the settings
    │   └── dependencies.py        #creating the vector and initializing the embedding model (all-MiniLM-L6-v2)
    ├── models
    │   └── pydantic_models.py     #dto the input and the output format
    └── services
        ├── generation_service.py  #generate the response
        ├── rag_service.py         #retrive and rerank
        ├── pipeline.py            #initialize the vector_store
        └── processing.py          #the Document processor
```