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

---

##  RAG Workflow

### 1️ Document Loading
Documents are loaded with LangChain loaders such as:

- `PyPDFLoader`
- Custom cleaning logic to remove:
  - Headers and footers  
  - Duplicated lines  
  - Page numbers  
  - OCR artifacts

---

## 2 Hybrid Chunking Strategy

This system uses a **hybrid multi-layer chunking strategy**:

### 2.1 Structural Chunking
Chunks follow natural structure:
- Titles
- Headings (H1, H2, H3)
- Paragraph boundaries
- Section hierarchy

### 2.2  Semantic Chunking
Using `SemanticChunker` with **all-MiniLM-L6-v2** embeddings to split at meaningful semantic transitions.

### 2.3  Adaptive Chunking
Chunk size adjusts depending on the content type:
- Bullet lists → small chunks  
- Procedures → isolated blocks  
- Narrative sections → larger chunks  
- Dense paragraphs → medium chunks  

### 2.4  Metadata Augmentation
Each chunk includes:
- File name  
- Page number  
- Section name  
- Structural level  
- Token length  

This improves retrieval and reranking accuracy.

---

## 3 Vector Store — ChromaDB

Chunks are embedded using **all-MiniLM-L6-v2** and stored in a persistent ChromaDB instance.

Stored items include:
- Embeddings  
- Raw text  
- Metadata  

Vector search uses cosine similarity.

---

## 4 Re-ranking with Cross-Encoder

After ChromaDB returns the top-k candidates:

1. Each chunk is paired with the user query.  
2. A **Cross-Encoder** model (MS Marco / similar) scores relevance.  
3. Chunks are **sorted by score**, not by embedding similarity.  
4. Only top-ranked chunks are chosen as final context.  

This drastically increases retrieval precision, especially for:
- Technical manuals  
- Step-by-step procedures  
- Regulatory documents  

---

## 5 Generation with Gemini API

Gemini receives:
- The top re-ranked chunks  
- Rich metadata  
- A structured prompt  
- Safety and grounding instructions  

Gemini then produces an answer with source mapping.

---

## 🔍 Retrieval Pipeline Summary
[ User Query ]
        ↓
[ Embed Query (all-MiniLM-L6-v2) ]
        ↓
[ Vector Search in ChromaDB ]
        ↓
[ Retrieve Top 8–12 Chunks ]
        ↓
[ Cross-Encoder Re-ranking ]
        ↓
[ Select Top 3–5 Chunks ]
        ↓
[ Send to Gemini API ]
        ↓
[ Final Answer + Source Citations ]
---

## Features

- Works with PDF, DOCX, TXT, manuals, and reports  
- Hybrid chunking for maximal semantic integrity  
- Cross-encoder improves ranking accuracy  
- Metadata-rich indexing for better grounding  
- Uses Gemini for final natural-language responses  
- Clean, modular structure  

---

##  Challenges & Solutions

### Poor results with fixed-size chunking  
**Solution:**  
Use structural + semantic + adaptive chunking to preserve meaning.

### Vector search returned noisy or unordered chunks  
**Solution:**  
Cross-Encoder reranking to score relevance like a human.

### PDF extraction contained noise  
**Solution:**  
Custom cleanup pipeline:
- Removing headers/footers  
- De-duplicating lines  
- Normalizing whitespace  

### Gemini context limits  
**Solution:**  
Strict top-k selection, reranking, and optional compression.

---
## Usage 
### 1.Clone the repo

```bash
git clone https://github.com/YoussefNKH/flightmanual-rag.git

cd flightmanual-rag

```
### 2.Create virtual envirement
```bash
python -m venv .venv

```
### 2.1.Activate the  virtual envirement
**windows**

```bash
.venv\Scripts\activate

```

**linux&Macos**


```bash
source .venv/bin/activate

```
### 3. Install dependencies

```bash

pip install -r requirements.txt

```
## 4. Environment Variables

Create a `.env` file in the root of your project and add your Gemini API key:

```env

GEMINI_API_KEY="your-key-here"

```
## 5. Run the server

```bash

python -m app.main

```

