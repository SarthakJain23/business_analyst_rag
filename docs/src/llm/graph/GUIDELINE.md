# 📄 Guideline: `src/llm/graph.py` — LangGraph RAG Workflow

> **File**: [`graph.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/graph.py)
> **Lines**: 160 | **Role**: Defines the LangGraph state machine for tool-calling RAG
> **Module**: `src.llm`

---

## 1. High-Level Overview

### Purpose
`graph.py` defines the **LangGraph stateful workflow** that powers the RAG agent. It:
1. Creates a tool-callable function (`search_business_documents`) bound to the vector store
2. Builds a `StateGraph` with a single `agent` node that invokes the LLM with tools
3. Compiles the graph into an executable application

### Architectural Role
This is the **declarative workflow definition** layer. It is used by `RAGEngine.query()` (the synchronous path) to execute queries through a proper LangGraph state machine. The streaming path in `rag_engine.py` bypasses this graph and manages the tool-calling loop manually.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **State Machine** | `StateGraph` from LangGraph defines states and transitions |
| **Tool Pattern** | `@tool` decorator creates LangChain-compatible tool functions |
| **Factory Function** | `build_rag_graph()` is a factory that constructs and compiles the workflow |
| **Closure** | `create_document_search_tool()` uses closures to capture `vector_store`, `top_k`, etc. |

---

## 2. Dependencies & Imports

### External Libraries
| Import | Purpose |
|--------|---------|
| `langchain_core.messages` | `BaseMessage`, `HumanMessage`, `SystemMessage` |
| `langchain_core.tools.tool` | `@tool` decorator for LangChain tools |
| `langchain_google_genai.ChatGoogleGenerativeAI` | Google Gemini LLM wrapper |
| `langgraph.graph` | `StateGraph`, `START`, `END` for workflow definition |

### Internal Modules
| Import | Purpose |
|--------|---------|
| `src.config.settings` | API key, model defaults |
| `src.llm.prompts.BUSINESS_ANALYST_SYSTEM_PROMPT` | System prompt for the agent |
| `src.vector_store.store.VectorStoreManager` | Vector store search interface |
| `src.utils.logger` | Logging |

---

## 3. Low-Level Breakdown

### 3.1 `extract_text_content()` (Lines 20–32)
```python
def extract_text_content(content: Any) -> str:
```
Handles three content formats returned by Gemini:
- **`str`**: Direct passthrough
- **`list`**: Iterates items, extracts `dict["text"]` or raw strings, joins them
- **Other/None**: Converts to string or returns empty

> **Note**: This function is **duplicated** in `rag_engine.py` (Lines 21–33). Should be extracted to a shared utility.

### 3.2 `strip_thinking_tags()` (Lines 35–40)
```python
def strip_thinking_tags(text: str) -> str:
```
- Detects `<thinking>...</thinking>` blocks in the LLM response
- Strips the thinking block and returns only the content **after** `</thinking>`
- Used for non-streaming responses where thinking content is not displayed separately

### 3.3 `RAGState` TypedDict (Lines 43–51)
```python
class RAGState(TypedDict):
    question: str
    chat_history: str
    top_k: int
    similarity_threshold: float
    temperature: float
    messages: List[BaseMessage]
    citations: List[Dict[str, Any]]
    generation: str
```

This defines the **state schema** for the LangGraph workflow:

| Field | Type | Direction | Purpose |
|-------|------|-----------|---------|
| `question` | `str` | Input | User's query |
| `chat_history` | `str` | Input | Serialized conversation context |
| `top_k` | `int` | Input | Number of chunks to retrieve |
| `similarity_threshold` | `float` | Input | Minimum similarity score |
| `temperature` | `float` | Input | LLM generation temperature |
| `messages` | `List[BaseMessage]` | I/O | LangChain message history (built in-node) |
| `citations` | `List[Dict]` | Output | Source citations from tool calls |
| `generation` | `str` | Output | Final cleaned response text |

### 3.4 `create_document_search_tool()` (Lines 54–104)
```python
def create_document_search_tool(
    vector_store, top_k, similarity_threshold, citations_list
):
```

**Factory function** that returns a `@tool`-decorated function with the following behavior:

1. **Empty store check** (Lines 65–67): Returns instruction message if no documents indexed
2. **Vector search** (Lines 69–73): Calls `vector_store.search()` with configured parameters
3. **No results** (Lines 75–76): Returns "no relevant chunks found" message
4. **Citation extraction** (Lines 78–89): Appends citation dicts to the **shared mutable list** `citations_list`
5. **Format results** (Lines 91–102): Builds formatted source blocks:
   ```
   [Source #1: report.pdf | Location: Page 3 | Match Score: 0.87]
   <chunk text>
   ```

**Key Design**: The `citations_list` parameter is a **mutable list** passed by reference, allowing the tool function (called inside the LLM's tool-calling loop) to append citations that are later accessible in the outer scope.

### 3.5 `build_rag_graph()` (Lines 107–159)
```python
def build_rag_graph(vector_store, model_name=None):
```

**The main factory function** that constructs the LangGraph workflow.

#### `agent_node()` (Lines 111–151)
This is the **only node** in the graph. It:

1. **Extracts state** (Lines 112–116): Reads question, history, temperature, top_k, threshold from state
2. **Creates tool** (Lines 118–121): Builds `search_business_documents` tool bound to current parameters
3. **Configures LLM** (Lines 123–131):
   ```python
   llm = ChatGoogleGenerativeAI(**llm_kwargs)
   llm_with_tools = llm.bind_tools([search_tool])
   ```
   - Skips temperature for Gemini 3.6 models (`"3.6" not in llm_model`)
4. **Builds prompt** (Lines 134–138): System message + Human message with chat history and question
5. **Invokes LLM** (Lines 145–146): Single synchronous call
6. **Cleans output** (Line 146): Strips thinking tags from response content
7. **Returns state update** (Lines 147–151): Updated messages, generation, and citations

#### Graph Construction (Lines 153–159)
```python
workflow = StateGraph(RAGState)
workflow.add_node("agent", agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)
app = workflow.compile()
```
- **Linear graph**: `START → agent → END` (no branching, no loops)
- The LLM handles tool-calling internally via `bind_tools()`, so no explicit tool node is needed

---

## 4. Data Flow

```
build_rag_graph(vector_store, model_name)
         │
         ▼
    StateGraph compiled
         │
         ▼
graph.invoke({question, chat_history, top_k, ...})
         │
         ▼
    agent_node:
         ├── Creates search tool (closure over vector_store)
         ├── Configures Gemini LLM + binds tools
         ├── Builds [SystemMessage, HumanMessage]
         ├── llm_with_tools.invoke(messages)
         │         │
         │         ├── (LLM decides: call tool or respond directly)
         │         ├── Tool call → search_business_documents(query)
         │         │         └── vector_store.search() → citations
         │         └── Response text
         │
         ▼
    {messages, generation, citations}
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Code Duplication** | `extract_text_content()` is duplicated in `rag_engine.py` | Extract to `src/utils/text.py` |
| **Graph Complexity** | Single-node graph doesn't leverage LangGraph's power (routing, loops, parallel nodes) | Add a router node that decides tool vs. direct response, and a tool-execution node |
| **Tool Calling** | `bind_tools()` handles tool calling in a single LLM turn; multi-turn tool use is not supported | Add a conditional edge that loops back to agent if tool calls are returned |
| **Temperature Hack** | `"3.6" not in llm_model` is a brittle string check | Use a model config registry or try/except on the parameter |
| **Caching** | LLM is re-instantiated on every `agent_node` invocation | Cache LLM instance at graph build time if temperature is fixed |
