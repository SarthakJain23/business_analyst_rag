# Utilities & Logging Module Guidelines (`logger.py`)

## Folder & Module Context

The [`src/utils/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/utils) directory provides shared logging utilities and helper functions used across all components of the system.

Centralizing logging configuration ensures that output timestamps, logger names, and log severity levels are formatted consistently across document loaders, ingestion orchestrators, vector database managers, and LLM streaming agents.

---

## Detailed Code Explanation & Function Breakdown

### Logger Factory: [`get_logger(name: str) -> logging.Logger`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/utils/logger.py#L5-L20)

```python
def get_logger(name: str = "business_analyst_rag") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger
```

- **Logic**:
  - `name`: Module name string identifying log origin (e.g., `"rag_engine"`, `"state_tracker"`, `"pdf_loader"`).
  - Checks `if not logger.handlers` to prevent adding duplicate handlers during repeated module imports.
  - Formats log lines: `2026-08-13 10:50:00 | INFO     | rag_engine | Starting query execution`.
  - Directs logs to `sys.stdout` stream handler.
