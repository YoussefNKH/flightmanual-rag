# Boeing 737 Flight Manual — RAG Service

Overview
- Retrieval-Augmented Generation (RAG) service to process Boeing 737 operations manuals, build a persistent Chroma vector index, and answer user queries via a generation model.
- Project code lives in `app/` — processors, pipeline, RAG logic, and FastAPI endpoints.

Hybrid chunking strategy
This project implements a hybrid chunking strategy that intentionally combines multiple techniques so the retrieval step returns coherent, safe and traceable passages:

- Structural chunking (respect document hierarchy): the splitter prioritizes natural manual boundaries (sections, procedures, checklists, safety annotations). This avoids splitting step-by-step procedures or safety-critical text across chunks when possible.

- Semantic chunking (preserve meaning boundaries): sentence- and word-level separators act as fallbacks to keep semantic units intact and reduce mid-sentence splits.

- Adaptive chunking (adjust to content type): chunk size and overlap adapt to the content — for example larger chunks for performance tables (so rows/columns remain intact) and single-chunk preservation for short procedures/checklists (kept whole when <= 1.5× chunk_size).

- Metadata augmentation (enhanced retrieval context): every chunk includes rich metadata (source, page number, chapter/section, content_type, safety annotations, detected systems, chunk index, total_chunks, flags like `has_performance_data`/`has_checklist`). This supports precise filtering and explainability in responses.

Splitter and defaults
- Splitter: `RecursiveCharacterTextSplitter` with a hierarchical separator list such as `"\n\n\n"`, `"\nProcedure\n"`, `"\nChecklist\n"`, `"\nWARNING:"`, `"\nCAUTION:"`, `"\nNote:"`, `"\n\n"`, `"\n"`, `". "`, `" "`, `""`.
- Defaults: `chunk_size = 800` characters and `chunk_overlap = 150` characters. When tables are detected we increase chunk_size (e.g., 2×) to keep tabular data coherent.

Why this approach works here
- Keeps procedural and safety-critical text intact for correct, auditable answers.
- Preserves semantics for natural language understanding and reduces hallucination risk stemming from chopped instructions.
- Metadata enables focused searches (by system, by safety level, by chapter) and makes results traceable back to pages/sections.

Core technologies used
- FastAPI: API endpoints and lifecycle management.
- LangChain: text splitting utilities and `Document` structures.
- ChromaDB: vector store and persistence (`vector_store/chroma_db`).
- HuggingFace embeddings: `sentence-transformers/all-MiniLM-L6-v2` used for chunk embeddings.
- SentenceTransformers / CrossEncoder: optional re-ranker to improve ordering after retrieval.
- GenAI / LLM: configurable generation model to produce the final answer from retrieved context.

Pipeline (high level)
1. Load PDF pages using `PyPDFLoader` and extract raw text.
2. Extract page-level metadata (chapter/section, warnings, systems, flags).
3. Apply hybrid chunking rules to generate chunks with metadata.
4. Embed chunks and index them in Chroma for efficient similarity search.
5. On query: retrieve candidates, rerank with CrossEncoder, assemble prompt context and call the LLM to generate the final answer with page sources.

Practical recommendations
- Avoid heavy document processing on startup in production; instead process on-demand or with a background worker.
- Version and backup the vector DB; re-index only when source docs change.
- Expose chunk metadata in API responses so consumers can validate and trace answers.
- Add unit tests to ensure the chunker preserves small procedures/checklists as single chunks.

Quick run
1. Create virtualenv and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the API (run from repository root):

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Config & files
- PDF sources: place in `data/documents/` (app expects a configured filename or will pick the first PDF in the folder at startup).
- Vector DB: `vector_store/chroma_db`.
- API keys: add to `.env` (see `.env.example`).

Next steps
- I can add a minimal `requirements.txt` and a unit test that verifies procedure-preservation by the chunker. Which would you like next?
