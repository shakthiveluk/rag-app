import os
import io
import tempfile
import traceback

import streamlit as st

from langchain_core.documents import Document

from ingest import ingest_pdf, split_documents, embed_and_store
from qa import answer_question


st.set_page_config(page_title="RAG over your file", page_icon="📄")
st.title("RAG over your file")

with st.sidebar:
	st.header("Instructions")
	st.markdown(
		"1) Upload a PDF or TXT file\n\n"
		"2) Click Ingest to index it in MongoDB\n\n"
		"3) Ask questions about the file"
	)
	st.caption(
		"Ensure your .env has MongoDB and model settings configured."
	)


def _ingest_text_content(file_name: str, text: str) -> int:
	"""Ingest raw text content by splitting into chunks and storing embeddings."""
	doc = Document(page_content=text, metadata={"source": file_name, "page": None})
	chunks = split_documents([doc])
	embed_and_store(chunks)
	return len(chunks)


uploaded = st.file_uploader(
	"Upload a file (PDF or TXT)", type=["pdf", "txt"], accept_multiple_files=False
)

ingested = st.session_state.get("ingested", False)
last_source = st.session_state.get("last_source", None)

col1, col2 = st.columns(2)
with col1:
	if st.button("Ingest", type="primary", disabled=uploaded is None):
		try:
			if uploaded is None:
				st.warning("Please upload a file first.")
				st.stop()

			fname = uploaded.name
			if fname.lower().endswith(".pdf"):
				with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
					# Write to a temp file path for PyPDFLoader
					tmp.write(uploaded.read())
					tmp_path = tmp.name
				count = ingest_pdf(tmp_path)
				os.unlink(tmp_path)
			elif fname.lower().endswith(".txt"):
				data = uploaded.read().decode("utf-8", errors="ignore")
				count = _ingest_text_content(fname, data)
			else:
				st.error("Unsupported file type. Please upload a PDF or TXT.")
				st.stop()

			st.success(f"Ingested {count} chunks from {fname}")
			st.session_state["ingested"] = True
			st.session_state["last_source"] = fname
		except Exception as e:
			st.error("Ingestion failed. See details in the expander below.")
			with st.expander("Error details"):
				st.code(traceback.format_exc())

with col2:
	if st.button("Clear session"):
		st.session_state.clear()
		st.rerun()

st.divider()

st.subheader("Ask a question about the uploaded file")
question = st.text_input("Your question", placeholder="e.g., What are the key skills?")

ask_disabled = not st.session_state.get("ingested", False)
if ask_disabled:
	st.info("Upload and ingest a file first.")

if st.button("Ask", disabled=ask_disabled) and question.strip():
	try:
		result = answer_question(question, k=4, prompt_name="default")
		st.markdown("**Answer**")
		st.write(result["answer"]) 

		st.markdown("**Sources**")
		for s in result["sources"]:
			with st.expander(f"{s['source']} (page={s['page']}) | chunk_id={s['chunk_id']}"):
				st.write(s["preview"]) 
	except Exception:
		st.error("Question answering failed. See details below.")
		with st.expander("Error details"):
			st.code(traceback.format_exc()) 