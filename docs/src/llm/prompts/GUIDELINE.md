# 📄 Guideline: `src/llm/prompts.py` — System Prompt Templates

> **File**: [`prompts.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/llm/prompts.py)
> **Lines**: 23 | **Role**: Centralizes LLM system prompts
> **Module**: `src.llm`

---

## 1. High-Level Overview

### Purpose
`prompts.py` defines the **system prompt** that instructs the LLM on its role, tool usage guidelines, thinking process, and response formatting. It is the "personality and behavior specification" for the RAG agent.

### Architectural Role
This is a **pure data module** — no logic, no classes, just string constants. It is imported by both `graph.py` and `rag_engine.py` to configure the LLM's system message.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Constant/Configuration Module** | System prompts as module-level constants |
| **Template Pattern** | The prompt is a structured template with sections (Tools, Guidelines, Thinking, Response) |

---

## 2. Dependencies & Imports

None — this is a pure constant module with zero imports.

---

## 3. Low-Level Breakdown

### 3.1 `BUSINESS_ANALYST_SYSTEM_PROMPT` (Lines 1–20)

The prompt is structured into four sections:

#### Section 1: Role Definition
```
You are an expert Senior Business Analyst, Corporate Strategist, and Financial Advisor
equipped with document search capabilities.
```
- Sets the LLM's persona as a senior business professional
- Mentions tool availability upfront

#### Section 2: Tool Invocation & Decision Guidelines
Three rules governing when to call `search_business_documents`:

| Rule | When to Apply | Action |
|------|---------------|--------|
| **Document-Specific Queries** | User asks about specific metrics, reports, financial numbers | Call `search_business_documents` tool |
| **General Concept Queries** | Greetings, definitions (EBITDA, DCF), general advice, math, coding | Respond directly (NO tool call) |
| **No Documents Available** | Tool returns "no documents indexed" | Inform user, encourage upload |

#### Section 3: Thinking Process Guideline
```
Before outputting your final response or invoking tools, output a step-by-step reasoning
thought process enclosed within <thinking> and </thinking> tags.
```
- Instructs the LLM to emit `<thinking>...</thinking>` blocks
- These are parsed by `ThinkingStreamParser` in `rag_engine.py` for UI display
- The `strip_thinking_tags()` function in `graph.py` removes them for non-streaming responses

#### Section 4: Final Response Guidelines
- **Executive Quality**: Structured markdown with headers, bold metrics, bullets, tables
- **Source Attribution**: Explicit citation format: `[Document: filename, Section: section]`

### 3.2 `TOOL_CALLING_ANALYST_SYSTEM_PROMPT` (Line 22)
```python
TOOL_CALLING_ANALYST_SYSTEM_PROMPT = BUSINESS_ANALYST_SYSTEM_PROMPT
```
- Currently an **alias** — identical to the main prompt
- Exists as a separate constant for potential future differentiation (e.g., different prompt for tool-calling vs. direct response paths)

---

## 4. Data Flow

```
prompts.py
    │
    ├──→ graph.py: agent_node() → SystemMessage(content=BUSINESS_ANALYST_SYSTEM_PROMPT)
    │
    └──→ rag_engine.py: query_stream() → SystemMessage(content=BUSINESS_ANALYST_SYSTEM_PROMPT)
```

---

## 5. Prompt Engineering Analysis

### Strengths
- Clear separation of tool-use vs. direct-response scenarios
- Thinking process instruction enables transparency in the UI
- Executive-quality formatting instruction produces professional output

### Weaknesses / Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Prompt Versioning** | No version tracking; changes can silently alter behavior | Add a `PROMPT_VERSION` constant and log it |
| **Dynamic Context** | Prompt doesn't include current date, document count, or available file list | Inject dynamic context at runtime (e.g., "You have access to N documents") |
| **Citation Format** | The citation format instruction conflicts with how citations are actually displayed in the UI | Align prompt citation format with UI rendering format |
| **Few-Shot Examples** | No examples of ideal responses | Add 1–2 few-shot examples for each scenario (tool use, direct response) |
| **Alias Constant** | `TOOL_CALLING_ANALYST_SYSTEM_PROMPT` is unused and identical | Remove it or differentiate it |
| **Thinking Tags** | Relying on the LLM to emit XML-like tags is fragile | Consider using Gemini's native thinking/reasoning mode if available |
