# LLM & RAG Engine - Guidelines

## Purpose
The `src/llm/` module interfaces with Google Gemini (`gemini-3.6-flash`), manages Business Analyst persona system prompts, constructs context-augmented prompts, and streams generated answers with explicit source citations.

## Structural Design & Guidelines

1. **Gemini Client (`client.py`)**:
   - Manages connection to `google-genai` / `google.generativeai` SDK using `GOOGLE_API_KEY` from config.
   - Configures model parameters (e.g. `gemini-3.6-flash` or fallback `gemini-2.5-flash`, temperature, top_p, max output tokens).

2. **System Prompts (`prompts.py`)**:
   - Instructs the Gemini model to act as a **Senior Business Analyst**.
   - Enforces analytical clarity, executive formatting (bullet points, key metrics, risk factors), table interpretation, and strict factual alignment based ONLY on retrieved context.
   - Rules: If context does not contain the answer, explicitly state that the documents do not provide sufficient information.

3. **RAG Pipeline (`rag_engine.py`)**:
   - Formats context blocks with document titles, page numbers, and chunk text.
   - Executes retrieval query against vector store.
   - Streams Gemini API responses to Streamlit UI.
   - Extracts and structures source citations (document name, page/sheet, snippet, similarity score) for presentation in expandable cards.

---
