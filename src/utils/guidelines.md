# Utilities & Logging Module - Guidelines

## Purpose
The `src/utils/` module provides cross-cutting helper functions and a centralized logging framework used across all components.

## Structural Design & Guidelines

1. **Logger Setup (`logger.py`)**:
   - Provides `get_logger(name: str)` function.
   - Formats log messages cleanly with timestamps, module names, log levels, and messages.
   - Outputs to console (`sys.stdout`) and optional log files in `data/logs/`.

2. **Error Handling**:
   - Wrap IO operations and API calls in try-except blocks.
   - Log errors with full traceback context before propagating or surfacing user-friendly messages in Streamlit.

---
