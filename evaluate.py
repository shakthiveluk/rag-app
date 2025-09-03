"""Simple evaluation harness using LangSmith criteria evaluators.

Enable LangSmith by setting these env vars:
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=ls__...
    LANGCHAIN_PROJECT=rag-mongo-demo
"""

from __future__ import annotations

from typing import List, Dict, Any

from langsmith import Client
from langchain.evaluation import load_evaluator

from qa import answer_question


def evaluate(samples: List[Dict[str, Any]]):
	"""Evaluate a list of samples with criteria: relevance, conciseness, groundedness.

	Each sample: {"question": str, "ground_truth": str (optional)}
	"""
	client = Client()
	evaluator = load_evaluator(
		"criteria", criteria=["relevance", "conciseness", "groundedness"]
	)
	results = []
	for s in samples:
		pred = answer_question(s["question"])  # default prompt
		ev = evaluator.evaluate_strings(
			prediction=pred["answer"],
			input=s["question"],
			reference=s.get("ground_truth", ""),
			context="\n\n".join([src["preview"] for src in pred["sources"]]),
		)
		results.append({"question": s["question"], "answer": pred["answer"], "eval": ev})
	return results


if __name__ == "__main__":
	samples = [
		{"question": "What programming languages am I proficient in?", "ground_truth": ""}
	]
	out = evaluate(samples)
	for r in out:
		print(r)


