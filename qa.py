"""Question-answering over MongoDB vector store using LangChain RAG.

Provides a retriever and a configurable RAG chain with swappable prompts.
"""

from __future__ import annotations

from typing import Dict, Any, List

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from config import get_llm, get_vectorstore
from prompts import PROMPTS


def _format_docs(docs: List[Document]) -> str:
	"""Join retrieved documents into a single context string with citations."""
	lines: List[str] = []
	for d in docs:
		src = d.metadata.get("source")
		page = d.metadata.get("page")
		chid = d.metadata.get("chunk_id")
		lines.append(f"[chunk_id={chid} | source={src} | page={page}]\n{d.page_content}")
	return "\n\n---\n\n".join(lines)


def get_retriever(k: int = 4):
	"""Return a similarity retriever over the MongoDB vector store."""
	vectorstore = get_vectorstore()
	return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})


def build_rag_chain(prompt_name: str = "default"):
	"""Create a RAG chain using the selected prompt template and current LLM."""
	llm = get_llm()
	if prompt_name not in PROMPTS:
		raise ValueError(f"Unknown prompt name: {prompt_name}. Available: {list(PROMPTS.keys())}")
	prompt = PROMPTS[prompt_name]()
	retriever = get_retriever()

	rag_chain = {
		"context": retriever | RunnableLambda(_format_docs),
		"question": RunnablePassthrough(),
	} | prompt | llm | StrOutputParser()

	return rag_chain, retriever


def answer_question(question: str, k: int = 4, prompt_name: str = "default") -> Dict[str, Any]:
	"""Retrieve, generate, and return answer along with source previews."""
	rag_chain, retriever = build_rag_chain(prompt_name)
	docs: List[Document] = retriever.get_relevant_documents(question)
	answer: str = rag_chain.invoke(question)
	return {
		"answer": answer,
		"sources": [
			{
				"chunk_id": d.metadata.get("chunk_id"),
				"source": d.metadata.get("source"),
				"page": d.metadata.get("page"),
				"preview": (d.page_content[:250] + "...") if len(d.page_content) > 250 else d.page_content,
			}
			for d in docs
		],
	}


