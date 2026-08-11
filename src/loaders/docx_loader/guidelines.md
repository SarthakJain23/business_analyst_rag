# Word Document Loader Guidelines & Explanation (`docx_loader.py`)

## Overview

The [`docx_loader.py`](docx_loader.py) module provides the `DocxLoader` class for ingesting Microsoft Word (`.docx`) files. It extracts text paragraphs and converts embedded Word tables into Markdown format.

## Class Definition

`DocxLoader` inherits from [`BaseLoader`](../base/base.py#L20) and implements `load(file_path: Path, file_hash: str) -> List[RawDocument]`.

---

## Detailed Code Flow & Guidelines

### 1. Document Loading

- Opens file using `docx.Document(file_path)` ([docx_loader.py:L15](docx_loader.py#L15)).

### 2. Paragraph Parsing

- Iterates over `doc.paragraphs` ([docx_loader.py:L19](docx_loader.py#L19)).
- Strips whitespace and appends non-empty text strings to `full_text`.

### 3. Table Formatting

- Iterates over `doc.tables` ([docx_loader.py:L24](docx_loader.py#L24)).
- Converts rows into Markdown table syntax (`| Cell 1 | Cell 2 |`) ([docx_loader.py:L28](docx_loader.py#L28)).
- Replaces internal cell newlines with spaces to avoid breaking table layout.

### 4. RawDocument Creation & Metadata

- Combines content using double newlines (`\n\n`) ([docx_loader.py:L31](docx_loader.py#L31)).
- Constructs metadata: `source_file`, `file_name`, `file_type`, `file_hash`, and `page_or_section: "Document Body"` ([docx_loader.py:L33-L39](docx_loader.py#L33-L39)).
- Returns [`RawDocument`](../base/base.py#L6) object.

### 5. Logging & Error Handling

- Logs success or handles exceptions and re-raises ([docx_loader.py:L42-L45](docx_loader.py#L42-L45)).
