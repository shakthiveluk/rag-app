"""PDF ingestion pipeline: load, split, embed, and store in MongoDB or FAISS.

Usage:
    from ingest import ingest_pdf
    count = ingest_pdf("resume.pdf")
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import get_vectorstore, get_embeddings, AppConfig

try:
	from langchain_community.vectorstores import FAISS  # type: ignore
	_HAS_FAISS = True
except Exception:
	_HAS_FAISS = False


def load_pdf(path: str) -> List[Document]:
	"""Load a PDF into a list of Documents, normalize minimal metadata."""
	loader = PyPDFLoader(path)
	docs = loader.load()
	for d in docs:
		# Normalize metadata
		d.metadata = {
			"source": Path(path).name,
			"page": d.metadata.get("page", None),
		}
	return docs


def split_documents(
	docs: List[Document], chunk_size: int = 900, chunk_overlap: int = 150
) -> List[Document]:
	"""Split documents into overlapping chunks with stable chunk ids."""
	splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap,
		add_start_index=True,
	)
	chunks = splitter.split_documents(docs)
	for c in chunks:
		raw = f"{c.page_content}|{c.metadata.get('source')}|{c.metadata.get('page')}"
		chunk_id = hashlib.md5(raw.encode("utf-8")).hexdigest()
		c.metadata["chunk_id"] = chunk_id
	return chunks


def embed_and_store(chunks: List[Document]) -> None:
	"""Create embeddings and store chunks in configured vector store.

	For ATLAS: add documents to MongoDB Atlas Vector Search vector store.
	For FAISS: build/save a local FAISS index under FAISS_INDEX_DIR.
	"""
	cfg = AppConfig()
	embeddings = get_embeddings(cfg)

	if cfg.vectorstore_provider == "FAISS":
		if not _HAS_FAISS:
			raise ValueError("FAISS not installed. Please install faiss-cpu.")
		index_dir = cfg.faiss_index_dir
		os.makedirs(index_dir, exist_ok=True)
		faiss_store = FAISS.from_documents(chunks, embeddings)
		faiss_store.save_local(index_dir)
		return

	# Default: Atlas
	vectorstore = get_vectorstore(cfg)
	ids = [c.metadata["chunk_id"] for c in chunks]
	vectorstore.add_documents(documents=chunks, ids=ids)


def ingest_pdf(path: str) -> int:
	"""End-to-end ingestion for a single PDF; returns number of chunks stored."""
	docs = load_pdf(path)
	chunks = split_documents(docs)
	embed_and_store(chunks)
	return len(chunks)


