### RAG Web App: Architecture and Flow

This document explains how the app ingests your files, indexes them for retrieval, answers questions grounded in the uploaded content, and how each part of the codebase works together.

## Overview

- **Goal**: Upload a PDF/TXT and ask questions answered from the document content (RAG: Retrieval-Augmented Generation).
- **Core flow**:
  1. Upload file in the Streamlit UI (`app.py`).
  2. Ingest: load → split into chunks → embed → store in a vector store (`ingest.py`).
  3. Retrieve top-k chunks for a question from the vector store (`qa.py`).
  4. Build a RAG chain (prompt + LLM), generate an answer grounded in retrieved context (`qa.py`, `prompts.py`).
  5. Display the final answer and sources in the UI (`app.py`).

## Project layout (key files)

- `app.py`: Streamlit web UI (upload → ingest → Q&A)
- `ingest.py`: PDF/TXT ingestion pipeline (chunking, embedding, persisting)
- `qa.py`: Retriever and RAG chain assembly; answer formatting with sources
- `prompts.py`: Prompt templates for the LLM
- `config.py`: Environment-driven configuration; providers for embeddings/LLM/vectorstore
- `requirements.txt`: Python dependencies

## Configuration and providers (`config.py`)

- Reads env vars (via `python-dotenv`) to select providers and settings.
- **Embeddings**: `OPENAI` (default) or `HF` (Hugging Face)
- **LLM**: `OPENAI` (default) or `OLLAMA`
- **Vector store**: `ATLAS` (MongoDB Atlas Vector Search) or `FAISS` (local index)

Key functions:

- `get_embeddings`: returns OpenAI or HuggingFace embeddings depending on `EMBEDDINGS`.
- `get_llm`: returns ChatOpenAI or ChatOllama depending on `LLM_PROVIDER`.
- `get_vectorstore`:
  - `ATLAS`: creates a `MongoDBAtlasVectorSearch` over the configured collection and index.
  - `FAISS`: loads a local FAISS index from `FAISS_INDEX_DIR`.

Important env vars:

- Vector store
  - `VECTORSTORE`: `ATLAS` or `FAISS`
  - `FAISS_INDEX_DIR`: local FAISS directory (default `.faiss_index`)
  - For Atlas: `MONGODB_URI`, `MONGODB_DB`, `MONGODB_COLLECTION`, `MONGODB_ATLAS_INDEX_NAME`
- Models
  - `EMBEDDINGS`: `OPENAI` or `HF`
  - `LLM_PROVIDER`: `OPENAI` or `OLLAMA`
  - `OPENAI_API_KEY`, `OPENAI_MODEL`
  - `HF_EMBEDDINGS_MODEL`
  - `OLLAMA_MODEL`

## Ingestion pipeline (`ingest.py`)

Steps when you click Ingest in the UI:

1. Load the file into `Document` objects (for PDF via `PyPDFLoader`). Metadata is normalized to include:
   - `source` (file name)
   - `page` (for PDFs)
2. Split documents into overlapping chunks using `RecursiveCharacterTextSplitter`.
3. Assign a stable `chunk_id` to each chunk (MD5 over content+metadata) to deduplicate and cite.
4. Embed and persist:
   - `FAISS` mode: build a FAISS index and save to `FAISS_INDEX_DIR`.
   - `ATLAS` mode: write chunks to MongoDB and let Atlas Vector Search index them.

Why chunking? Improves retrieval granularity and avoids hitting token limits with large documents.

## Retrieval and RAG chain (`qa.py`)

- `get_retriever(k)`: wraps the vector store as a similarity retriever.
- `_format_docs`: renders retrieved chunks into a context string with citations (chunk id, source, page).
- `build_rag_chain(prompt_name)`: composes a runnable chain:
  - Inputs: `{ "context": retriever | format_docs, "question": passthrough }`
  - Then: selected prompt template → LLM → string parser.
- `answer_question(question, k, prompt_name)`: executes retrieval + generation, and returns:
  - `answer` (string)
  - `sources` (list of cited chunks with `chunk_id`, `source`, `page`, `preview`)

Note: You may see a deprecation warning about `get_relevant_documents`; it still works. A future refactor can switch to `retriever.invoke(question)` to silence the warning.

## Prompt templates (`prompts.py`)

- `PROMPTS` maps names to prompt factories:
  - `default`: balanced, grounded, concise, cites when useful.
  - `strict`: only answer from context; otherwise say "I don't know based on the provided documents."
- You can change the active prompt by passing `prompt_name` to `answer_question`.

## Web UI flow (`app.py`)

- Upload area accepts PDF or TXT.
- Ingest button:
  - PDF: temporarily saves upload → `ingest_pdf` → deletes temp file.
  - TXT: constructs a `Document` → reuses split + embed + store.
  - Sets `st.session_state["ingested"] = True` to enable Q&A.
- Q&A section:
  - Sends your question to `answer_question`.
  - Displays the answer and expandable source previews (chunk id, source, page, preview text).
- Clear session button:
  - Clears session state and calls `st.rerun()` to reset the app view.

## Running the app

FAISS (local index, no database required):

```bash
cd "/home/shakthivelu/Documents/Learning ai/Langchain"
source .venv/bin/activate
export VECTORSTORE=FAISS
streamlit run app.py --server.port=8501
```

Open `http://localhost:8501`.

MongoDB Atlas Vector Search:

1. Ensure the Atlas index exists on the collection (example schema):

```json
{
	"fields": [
		{
			"type": "vector",
			"path": "embedding",
			"numDimensions": 1536,
			"similarity": "cosine"
		},
		{ "type": "filter", "path": "text" }
	]
}
```

2. Set env vars and run:

```bash
export VECTORSTORE=ATLAS
export MONGODB_URI='mongodb+srv://...'
export MONGODB_DB='rag_demo'
export MONGODB_COLLECTION='documents'
export MONGODB_ATLAS_INDEX_NAME='vector_index'
streamlit run app.py --server.port=8501
```

## Troubleshooting

- `$vectorSearch stage is only allowed on MongoDB Atlas`:
  - Use `VECTORSTORE=FAISS` to run locally without Atlas; or run against a MongoDB Atlas cluster with a vector index.
- `st.experimental_rerun` not found:
  - The app uses `st.rerun()` (Streamlit ≥1.27). Upgrade Streamlit or keep current code.
- OpenAI key issues:
  - Ensure `OPENAI_API_KEY` is set and your model (`OPENAI_MODEL`) is supported.
- No results / poor answers:
  - Increase `k` in `answer_question`; adjust chunk size/overlap; ensure the file was ingested and the FAISS directory exists.

## Extending

- Add more loaders: DOCX (`langchain_community.document_loaders.Docx2txtLoader`), CSV (`CSVLoader`), HTML, etc.
- Swap providers: set `EMBEDDINGS=HF` or `LLM_PROVIDER=OLLAMA`.
- UI improvements: multi-file ingestion, history, citations with clickable anchors.
- Silence deprecation warnings: replace `retriever.get_relevant_documents(q)` with `retriever.invoke(q)`.

## Attributions

- Built with LangChain, Streamlit, FAISS, and MongoDB Atlas Vector Search (optional).
