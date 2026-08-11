# Text & Markdown Loader Guidelines & Explanation (`text_loader.py`)

## Overview

The [`text_loader.py`](text_loader.py) module defines the `TextLoader` class, which handles loading and parsing of plain text (`.txt`) and Markdown (`.md`) files into [`RawDocument`](../base/base.py#L6) objects.

---

## Class Definition & Code Flow

### 1. Class Inheritance ([text_loader.py:L8](text_loader.py#L8))

`TextLoader` inherits from [`BaseLoader`](../base/base.py#L20) and implements `load(file_path: Path, file_hash: str) -> List[RawDocument]`.

### 2. File Reading & Encoding ([text_loader.py:L14-L15](text_loader.py#L14-L15))

- Opens file with UTF-8 encoding: `open(file_path, "r", encoding="utf-8", errors="replace")`.
- Uses `errors="replace"` to gracefully handle non-UTF8 or malformed text characters without throwing decoding exceptions.
- Reads file content and trims surrounding whitespace via `.strip()`.

### 3. RawDocument & Metadata Construction ([text_loader.py:L17-L25](text_loader.py#L17-L25))

If content is non-empty, creates metadata:

- `source_file`: Absolute resolved file path (`str(file_path.resolve())`).
- `file_name`: File name string (`file_path.name`).
- `file_type`: Lower-case file suffix (`.txt` or `.md`).
- `file_hash`: SHA-256 hash string for state tracking.
- `page_or_section`: `"Document Content"`.

Wraps content and metadata inside a [`RawDocument`](../base/base.py#L6) object and appends it to the return list.

### 4. Logging & Error Handling ([text_loader.py:L27-L30](text_loader.py#L27-L30))

- Emits success log message via `logger.info`.
- Catches runtime exceptions, logs details via `logger.error`, and re-raises exceptions.
