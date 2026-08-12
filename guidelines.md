# Business Analyst RAG Application - Master Project Guidelines

## Overview

This document outlines the design principles, architectural standards, directory structure, and engineering practices for the **Business Analyst RAG** system.

The core objective of this project is to provide a clean, production-ready, modular RAG pipeline tailored for business document analysis (financial statements, market research, strategic decks, CSV/Excel data tables, meeting notes) with automated incremental file ingestion, local ChromaDB storage, live thinking process streaming, and an autonomous Tool-Calling Agent workflow.

---

## Key Architectural Principles

1. **DRY (Don't Repeat Yourself)**:
   - Centralize configuration in [`src/config.py`](src/config.py).
   - Use unified Document datatypes and Factory patterns for document loading.
   - Avoid duplicating vector store or LLM initialization across modules.

2. **Orthogonality & Logical Separation**:
   - Each module handles a single, well-defined responsibility.
   - **Loaders**: Parse raw files into standard `Document` objects.
   - **Core Engine**: Manage chunking, SHA-256 state tracking, and pipeline execution.
   - **Vector Store**: Abstract vector persistence and query operations.
   - **LLM/RAG**: Orchestrate autonomous Tool-Calling agent workflows, system prompts, reasoning token parsing, and context synthesis.
   - **Streamlit App**: Presentation layer rendering Chat Center upload banners, real-time agent status, thinking token containers, and message history.

3. **Autonomous Tool-Calling Agent Architecture**:
   - Vector search is encapsulated into a formal tool (`search_business_documents`).
   - Gemini autonomously decides in a single streaming pass whether to call `search_business_documents` for document-specific questions or answer directly for general business concepts, greetings, and formulas.

4. **Live Thinking & Decision Process Streaming**:
   - Model reasoning enclosed within `<thinking>...</thinking>` tags is parsed token-by-token using `ThinkingStreamParser`.
   - Streaming events (`status`, `thought`, `answer`) are rendered inside an interactive Streamlit status widget (`🧠 Agent Thinking & Decision Process`) and preserved in message history.

5. **Chat Center Empty State Guidance**:
   - When no documents are uploaded or indexed (`has_documents = False`), the main Chat Center displays a central upload hero banner with drag-and-drop file upload and ingestion controls.

6. **Incremental & State-Aware Ingestion**:
   - File state is tracked using SHA-256 hashes in `data/metadata/ingestion_state.json`.
   - Re-ingesting untouched files is strictly avoided. Modified files trigger chunk replacement; deleted files trigger chunk eviction.

---

## Directory Structure & Sub-Guidelines Index

Click any link below to view the module-specific guidelines:

- 📂 [**src/loaders/guidelines.md**](src/loaders/guidelines.md)
  _Guidelines for document loaders, abstract parser interfaces, tabular data formatting, and metadata schema._

- 📂 [**src/core/guidelines.md**](src/core/guidelines.md)
  _Guidelines for incremental state tracking, chunking strategy, and the unified ingestion orchestrator._

- 📂 [**src/vector_store/guidelines.md**](src/vector_store/guidelines.md)
  _Guidelines for ChromaDB local persistence, Gemini embedding generation (`gemini-embedding-001`), and similarity retrieval._

- 📂 [**src/llm/guidelines.md**](src/llm/guidelines.md)
  _Guidelines for Google Gemini (`gemini-3.6-flash`), Tool-Calling Agent graph (`graph.py`), `ThinkingStreamParser`, prompt engineering, and streaming execution (`rag_engine.py`)._

- 📂 [**src/utils/guidelines.md**](src/utils/guidelines.md)
  _Guidelines for logging standards, exception handling, and shared helper routines._

---

## Development Environment & Workflow

- **Environment Manager**: [`uv`](https://github.com/astral-sh/uv)
- **Virtual Environment Creation**: `uv venv`
- **Dependency Installation**: `uv pip install -r requirements.txt` or `uv sync`
- **Execution**: `uv run streamlit run app.py`

---

