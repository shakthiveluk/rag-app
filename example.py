"""Minimal end-to-end example for the RAG pipeline.

Steps:
1) Ensure MongoDB Atlas Vector Search index exists for your collection.
2) Place a PDF named 'resume.pdf' in this directory.
3) Configure environment variables in .env
4) Run: python example.py
"""

from __future__ import annotations

import os

from config import AppConfig
from ingest import ingest_pdf
from qa import answer_question


def main() -> None:
	cfg = AppConfig()
	pdf_path = os.path.abspath("resume.pdf")
	if not os.path.exists(pdf_path):
		raise FileNotFoundError(
			f"Expected a PDF named 'resume.pdf' beside this script. Not found at {pdf_path}"
		)

	print("Ingesting PDF into MongoDB vector store...")
	num_chunks = ingest_pdf(pdf_path)
	print(f"Ingested {num_chunks} chunks from {pdf_path}")

	question = "What programming languages am I proficient in?"
	print(f"\nQuestion: {question}")
	result = answer_question(question, k=4, prompt_name="strict")

	print("\n=== Answer ===")
	print(result["answer"]) 

	print("\n=== Sources ===")
	for s in result["sources"]:
		print(f"- chunk_id={s['chunk_id']} source={s['source']} page={s['page']}")
		print(f"  preview: {s['preview'][:160]}")


if __name__ == "__main__":
	main()


