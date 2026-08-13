# 📄 Guideline: `app.py` — Streamlit Application Entry Point

> **File**: [`app.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/app.py)
> **Lines**: 393 | **Role**: Application entry point & UI layer
> **Module**: Root (not inside `src/`)

---

## 1. High-Level Overview

### Purpose
`app.py` is the **single entry point** for the entire Business Analyst RAG application. It implements a full-featured **Streamlit web application** that provides:

- Document upload & management (sidebar)
- Incremental ingestion triggering
- Conversational chat interface with streaming LLM responses
- RAG configuration controls (model, temperature, top-k, similarity threshold)
- Citation display and agent thinking visualization
- Memory/data reset functionality

### Architectural Role
This file acts as the **Controller + View** in an MVC-like pattern. It:
1. **Instantiates** all backend services (`StateTracker`, `VectorStoreManager`, `IngestionEngine`, `RAGEngine`) via Streamlit session state
2. **Orchestrates** user interactions (upload → ingest → query → display)
3. **Renders** the entire UI including sidebar controls, chat history, and streaming responses

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Session State Singleton** | Each service is created once per session via `st.session_state` guards |
| **Observer/Event-Driven** | Streamlit's reactive re-run model triggers UI updates on state changes |
| **Mediator** | `app.py` mediates between all backend components without them knowing about each other |

---

## 2. Dependencies & Imports

### External Libraries
| Import | Purpose |
|--------|---------|
| `time` | Artificial progress bar delays during ingestion |
| `streamlit` | Web UI framework (reactive, widget-based) |

### Internal Modules
| Import | Purpose |
|--------|---------|
| `src.config.settings` | Centralized configuration (paths, model names, thresholds) |
| `src.core.ingestion.IngestionEngine` | Orchestrates document loading → chunking → vector indexing |
| `src.core.state_tracker.StateTracker` | Tracks file hashes for incremental ingestion |
| `src.llm.rag_engine.RAGEngine` | Tool-calling RAG pipeline with streaming support |
| `src.vector_store.store.VectorStoreManager` | ChromaDB vector store operations |

---

## 3. Low-Level Breakdown

### 3.1 Page Configuration (Lines 12–17)
```python
st.set_page_config(
    page_title="Business Analyst RAG - Gemini",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
```
- Sets browser tab title, favicon, and layout to `"wide"` (two-column)
- Sidebar starts expanded by default

### 3.2 Custom CSS Injection (Lines 20–61)
Injects raw CSS via `st.markdown(unsafe_allow_html=True)` for:
- `.main-title` — 2.2rem bold header
- `.sub-title` — Muted caption text
- `.hero-card` — Dashed-border upload prompt card
- `.citation-box` — Blue left-bordered citation block
- `.badge-indexed` — Green pill badge for indexed status

### 3.3 Session State Initialization (Lines 63–86)
```python
if "state_tracker" not in st.session_state:
    st.session_state.state_tracker = StateTracker()
```
Guards ensure each service is instantiated **exactly once** per browser session:

| Session Key | Type | Purpose |
|-------------|------|---------|
| `state_tracker` | `StateTracker` | File change detection |
| `vector_store` | `VectorStoreManager` | ChromaDB interface |
| `ingestion_engine` | `IngestionEngine` | Ingestion orchestrator |
| `rag_engine` | `RAGEngine` | LLM query pipeline |
| `messages` | `List[dict]` | Chat history for display |

**Line 84–86**: Reads current stats and document states to determine `has_documents` flag (used to show/hide the onboarding upload UI).

### 3.4 Sidebar — Document Management (Lines 88–138)
**File Upload** (Lines 97–112):
- `st.file_uploader` accepts: PDF, DOCX, XLSX, XLS, CSV, TXT, MD
- Writes uploaded files directly to `settings.DOCUMENTS_DIR`
- Shows success toast with file count

**Sync & Ingest Button** (Lines 115–138):
- Triggers `st.session_state.ingestion_engine.run()`
- Wraps in a two-phase progress bar (0→50 before, 50→100 after) for visual feedback
- Displays errors or success counts from `IngestionResult`
- Calls `st.rerun()` on success to refresh all UI state

### 3.5 Sidebar — Document Library State (Lines 141–158)
- Iterates `all_states` (from `StateTracker.get_all_states()`)
- Renders a `st.dataframe` with columns: File Name, Size (KB), Chunks, Status
- Shows info message if no documents indexed

### 3.6 Sidebar — RAG & Embedding Configuration
| Widget | Variable | Default | Range / Options |
|--------|----------|---------|-----------------|
| `st.selectbox` | `model_option` | `gemini-3.6-flash` | 4 Gemini models |
| `st.slider` | `temperature` | 0.2 | 0.0 – 1.0 |
| `st.slider` | `top_k` | `settings.TOP_K_RETRIEVAL` (5) | 1 – 15 |
| `st.slider` | `similarity_thresh` | `settings.SIMILARITY_THRESHOLD` (0.3) | 0.0 – 0.9 |
| `st.selectbox` | `selected_vendor_str` | `google` | Google Gemini, OpenAI |
| `st.selectbox` | `selected_model_str` | `gemini-embedding-001` | Model names for selected vendor |

- `set_model()` is called immediately on LLM selectbox change, rebuilding the LangGraph workflow if the model changed.
- **Vendor Change Detection**: When the user switches embedding vendor or model:
  - If no documents are currently indexed, the switch happens silently with `st.toast()`.
  - If documents are indexed, `@st.dialog("🔄 Confirm Embedding Vendor Switch")` is displayed to request confirmation before wiping existing embeddings and re-indexing.

### 3.7 Clear All & Vendor Switch Dialogs
- **`confirm_clear_dialog()`**: Prompts confirmation to permanently wipe chat history, vector index, metadata, and uploaded document files.
- **`confirm_vendor_switch_dialog(new_vendor, new_model)`**: Prompts confirmation to wipe existing ChromaDB vectors, reset embedding singleton via `reset_embedding_instance()`, re-initialize `VectorStoreManager`, and re-ingest all documents on disk using the newly selected vendor/model.

### 3.8 Main Panel — Onboarding (Lines 228–271)
- Renders title and subtitle with custom CSS classes
- When `has_documents == False`, shows an expanded upload area with:
  - File uploader (duplicate of sidebar, different `key`)
  - Sync button that triggers `ingestion_engine.run()`

### 3.9 Quick Starter Prompts (Lines 273–291)
Four pre-built business analysis prompts displayed as buttons:
1. 📊 Revenue & Growth Trends
2. ⚠️ Key Operational Risks
3. 📈 Table & Data Metrics
4. 📋 Executive Action Items

Clicking any button sets `selected_prompt` to the corresponding query string.

### 3.10 Chat History Rendering (Lines 293–311)
- Iterates `st.session_state.messages` and renders each with `st.chat_message`
- For assistant messages, optionally shows:
  - Agent thinking & decision process (in an expander)
  - Source citations with file name, page/section, similarity score, and snippet

### 3.11 Chat Input & Streaming Response (Lines 313–393)
**Input Handling** (Lines 314–316):
```python
prompt_input = st.chat_input("Ask a question...")
final_query = selected_prompt or prompt_input
```
Prioritizes button-selected prompts over text input.

**Streaming Pipeline** (Lines 324–386):
1. Creates a `st.status` container with three placeholders (status log, thought header, thought content)
2. Builds `history_str` from last 6 messages
3. Calls `rag_engine.query_stream()` which returns `(stream_iterator, citations)`
4. Iterates the stream, handling three event types:
   - `"status"` → Appended to status log
   - `"thought"` → Accumulated in thinking block
   - `"answer"` → Streamed to message placeholder with cursor (`▌`)
5. On completion, collapses status container and renders citation expander
6. Stores full response (with citations, thoughts, decision log) in session state

**Error Handling** (Lines 388–392):
- Catches all exceptions, updates status to error state, shows error message

---

## 4. Data Flow

```
User Upload → settings.DOCUMENTS_DIR (disk)
     │
     ▼
Sync Button → IngestionEngine.run()
     │
     ▼
User Query → RAGEngine.query_stream()
     │
     ├──→ "status" events → st.status container
     ├──→ "thought" events → thinking expander
     └──→ "answer" events → chat message (streamed)
     │
     ▼
Citations → expander with source details
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Separation of Concerns** | UI, state management, and business logic are tightly coupled in one 393-line file | Extract into separate modules: `ui/sidebar.py`, `ui/chat.py`, `ui/styles.py` |
| **Duplicate Upload Logic** | File upload code is duplicated between sidebar (L97–112) and main panel (L244–257) | Extract a `save_uploaded_files(files)` helper function |
| **CSS Management** | Inline CSS string in Python | Move to a separate `.css` file loaded via `st.markdown` |
| **Progress Bar** | Fake progress (sleep loops) doesn't reflect actual ingestion progress | Implement real progress callbacks from `IngestionEngine` |
| **Error Handling** | Bare `Exception` catch in clear dialog (L209) silently swallows errors | Log the exception at minimum |
| **Magic Numbers** | `[-6:]` for history window, `0.8` for sleep delay | Define as named constants in `settings` |
