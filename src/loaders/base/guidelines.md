# Base Loader Guidelines (`base.py`)

## Overview

The [`base.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py) module defines the abstract contract [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L20) and the standardized data structure [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L6) used across all file parsing components in the system.

---

## Guidelines & Architecture

### 1. Abstract Base Class (`BaseLoader`)

- All concrete document loaders (**PDF**, **Word**, **Excel/CSV**, **Text/Markdown**) MUST inherit from `BaseLoader`.
- Every loader class MUST implement the abstract method:
  `load(file_path: Path, file_hash: str) -> List[RawDocument]`

### 2. Standardized Document Data (`RawDocument`)

- Loaders MUST return a list of `RawDocument` dataclass instances.
- Standard required metadata fields for every document output:
  - `source_file`: Absolute resolved file path.
  - `file_name`: Basename of the file (e.g. `report.pdf`).
  - `file_type`: Lowercase file extension (e.g. `.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.md`).
  - `file_hash`: SHA-256 string for state tracking.
  - `page_or_section`: Section, page number (`Page 1`), or sheet name (`Sheet: Financials`).
