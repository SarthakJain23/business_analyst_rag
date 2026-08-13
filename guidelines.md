# Business Analyst RAG Application - Master Project Guidelines

## Folder & Repository Context

This repository houses the **Business Analyst RAG System**, an enterprise-grade document ingestion and autonomous AI agent platform tailored for analyzing complex business documents (financial filings, earnings reports, market research, Excel spreadsheets, CSV data tables, Word documents, and text notes).

The repository architecture is strictly modularized into functional components under [`src/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src):
- [`src/config.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/config.py): Application settings, directory paths, and model constants.
- [`src/loaders/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders): Document parsing submodules converting multi-format files into standardized document structures.
- [`src/core/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core): Incremental change detection via SHA-256 state tracking, text chunking, and unified ingestion workflow.
- [`src/vector_store/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/vector_store): ChromaDB local vector storage and Google Gemini embedding generation (`gemini-embedding-001`).
- [`src/llm/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm): Autonomous Tool-Calling Agent graph (`gemini-3.6-flash`), streaming reasoning token parser, and RAG execution pipeline.
- [`src/utils/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/utils): Logging and exception handling infrastructure.
- [`app.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/app.py): Streamlit web application user interface.

---

## Architectural Principles & Core Workflows

1. **DRY Configuration**: Centralized in [`Settings`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/config.py#L12-L39).
2. **Incremental Ingestion**: File modifications are tracked via SHA-256 checksums in [`StateTracker`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/state_tracker.py#L32-L148) saving vector re-computation.
3. **Autonomous Tool Routing**: Gemini autonomously decides whether to invoke [`search_business_documents`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/graph.py#L63-L104) or respond directly using system prompt guidelines ([`prompts.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/prompts.py#L1-L20)).
4. **Token Streaming & Thinking Isolation**: Uses [`ThinkingStreamParser`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/rag_engine.py#L36-L105) to separate model reasoning thoughts (`<thinking>`) from user-facing answer markdown.

---

## Directory Index & Sub-Guidelines

Click any link below to navigate to the respective module's guideline document:

- 📂 [**src/loaders/guidelines.md**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/guidelines.md) — Document loader interfaces, multi-format parsers, tabular data handling, and factory dispatching.
- 📂 [**src/core/guidelines.md**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/guidelines.md) — Incremental state tracking, text splitting, and unified ingestion engine orchestrator.
- 📂 [**src/vector_store/guidelines.md**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/vector_store/guidelines.md) — Local ChromaDB vector storage, Gemini embeddings, and ensemble hybrid search.
- 📂 [**src/llm/guidelines.md**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/guidelines.md) — LangGraph Tool-Calling Agent graph, thinking token stream parser, and multi-pass streaming generator.
- 📂 [**src/utils/guidelines.md**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/utils/guidelines.md) — Shared logger setup and error logging standards.

---

## Environment & Run Commands

- **Environment Manager**: [`uv`](https://github.com/astral-sh/uv)
- **Dependencies**: [`requirements.txt`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/requirements.txt) / [`pyproject.toml`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/pyproject.toml)
- **Run Application**: `uv run streamlit run app.py`
