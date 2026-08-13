# 📄 Guideline: `src/llm/rag_engine.py` — RAG Orchestrator & Streaming Engine

> **File**: [`rag_engine.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/rag_engine.py)
> **Lines**: 343 | **Role**: Main RAG query pipeline with streaming + tool-calling
> **Module**: `src.llm`

---

## 1. High-Level Overview

### Purpose
`rag_engine.py` is the **largest and most complex file** in the project. It implements the `RAGEngine` class, which provides two query paths:
1. **Synchronous** (`query()`) — Uses the LangGraph workflow from `graph.py`
2. **Streaming** (`query_stream()`) — Manually manages LLM streaming, tool detection, tool execution, and synthesis in a generator function

It also contains the `ThinkingStreamParser` — a stateful parser that separates `<thinking>` blocks from answer text in real-time during streaming.

### Architectural Role
`RAGEngine` is the **primary interface** consumed by `app.py`. It encapsulates all LLM interaction complexity behind two methods. The streaming path is what the UI actually uses.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Facade** | `RAGEngine` provides a simple interface over LangGraph, LangChain, tool-calling, and streaming |
| **Strategy** | Two query strategies: synchronous (graph) and streaming (manual loop) |
| **Iterator/Generator** | `query_stream()` returns a Python generator yielding `(event_type, payload)` tuples |
| **State Machine** | `ThinkingStreamParser` is a mini state machine with `in_thinking` / `not_in_thinking` states |
| **Observer** | Yields status/thought/answer events for the UI to consume reactively |

---

## 2. Dependencies & Imports

### External Libraries
| Import | Purpose |
|--------|---------|
| `langchain_core.messages` | `HumanMessage`, `SystemMessage` |
| `langchain_core.tools.tool` | `@tool` decorator |
| `langchain_google_genai.ChatGoogleGenerativeAI` | Gemini LLM with streaming support |

### Internal Modules
| Import | Purpose |
|--------|---------|
| `src.config.settings` | API key, model defaults, retrieval params |
| `src.llm.graph.build_rag_graph` | LangGraph workflow builder (for sync path) |
| `src.llm.prompts.BUSINESS_ANALYST_SYSTEM_PROMPT` | System prompt |
| `src.vector_store.store.VectorStoreManager` | Vector store search |
| `src.utils.logger` | Logging |

---

## 3. Low-Level Breakdown

### 3.1 `extract_text_content()` (Lines 21–33)
**Duplicate** of the same function in `graph.py`. Handles string, list, and dict content from LLM responses.

### 3.2 `ThinkingStreamParser` Class (Lines 36–104)

A **stateful streaming parser** that separates `<thinking>...</thinking>` blocks from answer text in real-time.

#### State Machine
```
                     ┌─────────────────────┐
   ──────────────────│  not in_thinking     │
   text → ("answer") │  (initial state)     │
                     └─────────┬───────────┘
                               │ <thinking> found
                               ▼
                     ┌─────────────────────┐
   ──────────────────│  in_thinking         │
   text → ("thought")│                     │
                     └─────────┬───────────┘
                               │ </thinking> found
                               ▼
                     ┌─────────────────────┐
                     │  not in_thinking     │
                     │  (back to answer)    │
                     └─────────────────────┘
```

#### `feed(chunk: str)` Method (Lines 49–96)
- Appends `chunk` to internal `buffer`
- Loops to find `<thinking>` and `</thinking>` tags
- Emits `("thought", text)` for content inside thinking tags
- Emits `("answer", text)` for content outside thinking tags
- Handles **partial tag matching** (e.g., `<thin` at buffer end) via `_find_partial_tag()`

#### `_find_partial_tag()` Method (Lines 43–47)
```python
def _find_partial_tag(self, text: str, tag: str) -> int:
    for i in range(1, len(tag)):
        if text.endswith(tag[:i]):
            return len(text) - i
    return -1
```
- Checks if the buffer ends with a **prefix** of the target tag
- Prevents emitting partial tags as answer text (would look like `<think` in the UI)
- Returns index of the partial tag start, or -1 if none found

#### `flush()` Method (Lines 98–104)
- Emits any remaining buffered content after the stream ends
- Classifies remaining content based on current state (`in_thinking` or not)

### 3.3 `Citation` Dataclass (Lines 107–113)
```python
@dataclass
class Citation:
    file_name: str
    source_file: str
    page_or_section: str
    similarity_score: float
    snippet: str
```
Structured citation data used by the UI to display source references.

### 3.4 `RAGResponse` Dataclass (Lines 116–119)
```python
@dataclass
class RAGResponse:
    answer: str
    citations: List[Citation]
```
Return type for the synchronous `query()` method.

### 3.5 `RAGEngine` Class (Lines 122–342)

#### `__init__()` (Lines 125–132)
```python
def __init__(self, vector_store=None, model_name=None):
    self.vector_store = vector_store or VectorStoreManager()
    self.model_name = model_name or settings.GEMINI_LLM_MODEL
    self._graph = None  # Lazy-loaded
```

#### `graph` Property (Lines 134–138)
```python
@property
def graph(self):
    if self._graph is None:
        self._graph = build_rag_graph(self.vector_store, self.model_name)
    return self._graph
```
**Lazy initialization** — the LangGraph workflow is only compiled on first access.

#### `set_model()` (Lines 140–144)
```python
def set_model(self, model_name: str):
    if self.model_name != model_name:
        self.model_name = model_name
        self._graph = build_rag_graph(self.vector_store, self.model_name)
```
Rebuilds the graph when the model changes (called from UI selectbox).

#### `_extract_citations()` (Lines 146–160)
Converts raw chunk dicts to `Citation` dataclass instances. Truncates snippets to 300 chars.

#### `query()` — Synchronous Path (Lines 162–195)
```python
def query(self, user_query, chat_history_str, top_k, similarity_threshold, temperature):
```
1. Builds input state dict
2. Invokes the LangGraph workflow: `self.graph.invoke(input_state)`
3. Extracts `generation` and `citations` from output state
4. Converts raw citation dicts to `Citation` objects
5. Returns `RAGResponse`

#### `query_stream()` — Streaming Path (Lines 197–342)
```python
def query_stream(self, user_query, ...) -> Tuple[Iterator[Tuple[str, str]], List[Citation]]:
```

This is the **most complex method** and the one actually used by the UI.

**Returns**: `(generator, citations_list)` — the citations list is populated as a side-effect during generation.

##### Inner Tool Definition (Lines 211–243)
Defines `search_business_documents` as a `@tool` function with:
- Access to `self.vector_store` and query params via closure
- Citation extraction into the shared `citations` list
- Formatted source blocks as return value

##### `stream_generator()` Inner Function (Lines 245–340)

This is the **core streaming pipeline**:

1. **LLM Setup** (Lines 246–256): Creates Gemini LLM with `streaming=True`
2. **Prompt Construction** (Lines 258–263): System + Human message
3. **Initial Status Event** (Lines 265–268): Yields "Agent Thinking" status
4. **First-Pass Stream** (Lines 270–291):
   - Streams LLM response token-by-token
   - Detects tool calls from `chunk.tool_calls` or `chunk.additional_kwargs`
   - Feeds text through `ThinkingStreamParser` to separate thinking/answer
5. **Tool Execution** (Lines 293–335):
   - If tool calls detected:
     - Yields "Tool Invoked" status event
     - Manually invokes `search_business_documents.invoke({"query": ...})`
     - Yields "Tool Response Received" status event
     - **Second LLM call**: Streams a synthesis response with the tool results injected into the prompt
     - Second stream also goes through `ThinkingStreamParser`
   - If no tool calls:
     - Yields "Direct Senior Analyst Response" status

**Key Design Decision**: The streaming path **manually reimplements** tool-calling logic rather than using LangGraph's streaming. This is because LangGraph's streaming doesn't easily support the fine-grained event types (status, thought, answer) needed by the UI.

---

## 4. Data Flow

### Streaming Query Flow
```
query_stream(user_query, ...)
        │
        ├── Returns: (generator, citations_list)
        │
        ▼
  stream_generator() starts:
        │
        ├── Yield ("status", "Agent Thinking...")
        │
        ├── LLM.stream([SystemMessage, HumanMessage])
        │         │
        │         ├── Token chunks ──→ ThinkingStreamParser
        │         │                        ├── Yield ("thought", text)
        │         │                        └── Yield ("answer", text)
        │         │
        │         └── Tool calls detected?
        │                    │
        │            ┌──────┤──────────┐
        │            │ YES              │ NO
        │            ▼                  ▼
        │   Yield ("status", "Tool...") Yield ("status", "Direct...")
        │   search_tool.invoke()
        │   citations ← appended
        │   Yield ("status", "Synthesizing...")
        │   LLM.stream(synthesis prompt)
        │         │
        │         └── ThinkingStreamParser
        │              ├── Yield ("thought", text)
        │              └── Yield ("answer", text)
        │
        ▼
  Generator exhausted, citations populated
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Code Duplication** | `extract_text_content()` duplicated from `graph.py`; tool definition duplicated between graph and streaming | Extract shared code to `src/llm/tools.py` and `src/utils/text.py` |
| **Method Length** | `query_stream()` is 145 lines with deeply nested closures | Extract tool execution, LLM setup, and streaming into separate methods |
| **Tool Call Handling** | Only handles first tool call; doesn't support multi-tool or iterative tool-calling | Add a loop for multi-turn tool calling |
| **Citation Side Effects** | `citations` list is mutated inside a closure during generation | Consider yielding citations as events instead of relying on mutable state |
| **Error Handling** | No error handling inside `stream_generator()` | Add try/except to yield error events |
| **LangGraph Streaming** | Streaming path bypasses LangGraph entirely | Use LangGraph's `.stream()` or `.astream_events()` for native streaming with tool support |
| **Two LLM Calls** | Tool-calling path makes two separate LLM calls (initial + synthesis) | Use LangChain's `AgentExecutor` or LangGraph with tool nodes for single-pass tool calling |
