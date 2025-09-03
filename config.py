"""Configuration and factory utilities for the RAG app (LangChain + MongoDB).

This module centralizes environment configuration, and provides factory
functions to instantiate the Mongo collection, embeddings, LLM, and the
MongoDB Atlas Vector Search vector store used by LangChain.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient

# Embeddings and LLM providers
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

# Vector store integration for MongoDB Atlas Vector Search
from langchain_mongodb import MongoDBAtlasVectorSearch

# Optional local LLM via Ollama (only used if selected by env)
try:
	from langchain_community.chat_models import ChatOllama  # type: ignore
	_HAS_OLLAMA = True
except Exception:
	_HAS_OLLAMA = False

# Optional local FAISS vector store
try:
	from langchain_community.vectorstores import FAISS  # type: ignore
	_HAS_FAISS = True
except Exception:
	_HAS_FAISS = False


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
	"""Application configuration loaded from environment variables."""

	mongodb_uri: str = os.getenv("MONGODB_URI", "")
	db_name: str = os.getenv("MONGODB_DB", "rag_demo")
	collection_name: str = os.getenv("MONGODB_COLLECTION", "documents")

	# Vector store selection: ATLAS (MongoDB Atlas Vector Search) or FAISS (local)
	vectorstore_provider: str = os.getenv("VECTORSTORE", "FAISS").upper()
	faiss_index_dir: str = os.getenv("FAISS_INDEX_DIR", ".faiss_index")

	# Model/provider selection
	embeddings_provider: str = os.getenv("EMBEDDINGS", "HF").upper()
	llm_provider: str = os.getenv("LLM_PROVIDER", "OPENAI").upper()

	# OpenAI
	openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

	# Ollama (local)
	ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")

	# Hugging Face embeddings
	hf_model_name: str = os.getenv(
		"HF_EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
	)

	# MongoDB Atlas Vector Search index and field names
	search_index_name: str = os.getenv("MONGODB_ATLAS_INDEX_NAME", "vector_index")
	text_key: str = "text"
	embedding_key: str = "embedding"


def get_mongo_collection(cfg: Optional[AppConfig] = None):
	"""Return the MongoDB collection handle for the configured DB/collection."""
	cfg = cfg or AppConfig()
	if not cfg.mongodb_uri:
		raise ValueError("MONGODB_URI is not set")
	client = MongoClient(cfg.mongodb_uri)
	return client[cfg.db_name][cfg.collection_name]


def get_embeddings(cfg: Optional[AppConfig] = None):
	"""Instantiate the embeddings model based on configuration."""
	cfg = cfg or AppConfig()
	if cfg.embeddings_provider == "OPENAI":
		# text-embedding-3-small -> 1536 dims
		return OpenAIEmbeddings(model="text-embedding-3-small")
	if cfg.embeddings_provider == "HF":
		return HuggingFaceEmbeddings(model_name=cfg.hf_model_name)
	raise ValueError(f"Unsupported EMBEDDINGS provider: {cfg.embeddings_provider}")


def get_llm(cfg: Optional[AppConfig] = None):
	"""Instantiate the chat LLM based on configuration."""
	cfg = cfg or AppConfig()
	if cfg.llm_provider == "OPENAI":
		return ChatOpenAI(model=cfg.openai_model, temperature=0)
	if cfg.llm_provider == "OLLAMA":
		if not _HAS_OLLAMA:
			raise ValueError(
				"langchain_community ChatOllama not available. Install Ollama and its Python package."
			)
		return ChatOllama(model=cfg.ollama_model, temperature=0)
	raise ValueError(f"Unsupported LLM_PROVIDER: {cfg.llm_provider}")


def get_vectorstore(cfg: Optional[AppConfig] = None):
	"""Create or load the configured vector store.

	ATLAS: Uses MongoDB Atlas Vector Search over a collection.
	FAISS: Loads a local FAISS index directory (ingest will create/save it).
	"""
	cfg = cfg or AppConfig()
	embeddings = get_embeddings(cfg)

	if cfg.vectorstore_provider == "ATLAS":
		collection = get_mongo_collection(cfg)
		return MongoDBAtlasVectorSearch(
			collection=collection,
			embedding=embeddings,
			index_name=cfg.search_index_name,
			text_key=cfg.text_key,
			embedding_key=cfg.embedding_key,
		)

	if cfg.vectorstore_provider == "FAISS":
		if not _HAS_FAISS:
			raise ValueError("FAISS is not installed. Please install faiss-cpu.")
		if not os.path.isdir(cfg.faiss_index_dir):
			raise ValueError(
				f"FAISS index not found at {cfg.faiss_index_dir}. Ingest a file first."
			)
		return FAISS.load_local(
			cfg.faiss_index_dir, embeddings, allow_dangerous_deserialization=True
		)

	raise ValueError(
		f"Unsupported VECTORSTORE provider: {cfg.vectorstore_provider}. Use ATLAS or FAISS."
	)


