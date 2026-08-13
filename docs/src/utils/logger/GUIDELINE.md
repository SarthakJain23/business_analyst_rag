# 📄 Guideline: `src/utils/logger.py` — Logging Utility

> **File**: [`logger.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/utils/logger.py)
> **Lines**: 21 | **Role**: Provides configured loggers for all modules
> **Module**: `src.utils`

---

## 1. High-Level Overview

### Purpose
`logger.py` provides a `get_logger()` factory function that returns consistently configured Python `logging.Logger` instances. It is used by every module in the project for structured console output.

### Architectural Role
This is a **cross-cutting utility** — imported by all modules that need logging. It standardizes log format, level, and output destination across the entire application.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Factory Function** | `get_logger(name)` creates or retrieves a configured logger |
| **Singleton per Name** | Python's `logging.getLogger(name)` returns the same instance for the same name |
| **Idempotent Configuration** | `if not logger.handlers:` guard prevents duplicate handler registration |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `logging` | Python standard library logging |
| `sys` | Access to `sys.stdout` for console output |

---

## 3. Low-Level Breakdown

### 3.1 `get_logger()` Function (Lines 5–20)

```python
def get_logger(name: str = "business_analyst_rag") -> logging.Logger:
```

#### Step 1: Get or Create Logger (Line 7)
```python
logger = logging.getLogger(name)
```
- Python's `getLogger()` uses a **name-based registry** — same name returns same logger
- Default name: `"business_analyst_rag"` (the root logger for this application)

#### Step 2: Idempotent Handler Setup (Lines 8–18)
```python
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
```

**Guard**: `if not logger.handlers:` prevents adding multiple handlers when `get_logger()` is called multiple times with the same name (e.g., on Streamlit re-runs).

**Log Format**:
```
2025-08-13 21:30:15 | INFO     | ingestion_engine | Starting incremental ingestion cycle...
```

| Format Field | Syntax | Example |
|-------------|--------|---------|
| Timestamp | `%(asctime)s` | `2025-08-13 21:30:15` |
| Level | `%(levelname)-8s` | `INFO    ` (left-padded to 8 chars) |
| Logger Name | `%(name)s` | `ingestion_engine` |
| Message | `%(message)s` | `Starting incremental ingestion cycle...` |

**Output**: `sys.stdout` (console) — compatible with Streamlit's terminal output.

### Logger Names Used in the Project

| Module | Logger Name |
|--------|-------------|
| `src/core/ingestion/ingestion.py` | `"ingestion_engine"` |
| `src/core/state_tracker/state_tracker.py` | `"state_tracker"` |
| `src/llm/graph.py` | `"rag_graph"` |
| `src/llm/rag_engine.py` | `"rag_engine"` |
| `src/loaders/docx_loader/docx_loader.py` | `"docx_loader"` |
| `src/loaders/excel_loader/excel_loader.py` | `"excel_loader"` |
| `src/loaders/pdf_loader/pdf_loader.py` | `"pdf_loader"` |
| `src/loaders/text_loader/text_loader.py` | `"text_loader"` |
| `src/vector_store/store.py` | `"vector_store"` |

---

## 4. Data Flow

```
Any module:
  from src.utils.logger import get_logger
  logger = get_logger("module_name")
  logger.info("message")
       │
       ▼
  StreamHandler → sys.stdout → console
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **File Logging** | Only outputs to console; logs are lost when terminal closes | Add a `FileHandler` writing to `data/logs/app.log` with rotation |
| **Log Level Configuration** | Hardcoded to `INFO` | Make configurable via `settings` or environment variable (e.g., `LOG_LEVEL=DEBUG`) |
| **Structured Logging** | Plain text format is hard to parse programmatically | Consider `structlog` or JSON formatter for production use |
| **Streamlit Compatibility** | Streamlit captures `stdout`; some logs may not appear correctly | Test with Streamlit's logger integration |
| **Log Rotation** | No rotation for file-based logging (N/A currently) | Use `RotatingFileHandler` or `TimedRotatingFileHandler` when adding file logging |
| **Centralized Config** | Each module calls `get_logger()` independently | Consider using `logging.config.dictConfig()` for centralized setup |
