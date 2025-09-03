"""Prompt templates for grounded RAG responses.

You can define multiple prompt templates here and reference them by name
when building the RAG chain. This lets you quickly A/B test groundedness
and hallucination behavior.
"""

from langchain_core.prompts import ChatPromptTemplate


def grounded_default_prompt() -> ChatPromptTemplate:
	"""Balanced prompt: grounded and concise, cites when useful."""
	return ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"You are a careful assistant. Answer the user using only the provided context. "
				"If the answer cannot be found, say you do not know. "
				"Cite sources by chunk id and page when useful.",
			),
			(
				"human",
				"Question: {question}\n\n"
				"Context:\n{context}\n\n"
				"Rules:\n- Use only the context.\n- Be concise.\n- If insufficient context, say 'I don't know.'",
			),
		]
	)


def more_strict_no_hallucinations_prompt() -> ChatPromptTemplate:
	"""Strict prompt: never speculate; must only answer from context."""
	return ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"You must only answer from the provided context. If the context is insufficient, "
				"reply exactly: 'I don't know based on the provided documents.' Include citations for any claims.",
			),
			(
				"human",
				"Answer the question strictly from the context.\nQuestion: {question}\n\nContext:\n{context}",
			),
		]
	)


PROMPTS = {
	"default": grounded_default_prompt,
	"strict": more_strict_no_hallucinations_prompt,
}


