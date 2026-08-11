# PDF Loader Guidelines & Code Explanation (`pdf_loader.py`)

## Overview

The [`pdf_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py) module defines the `PDFLoader` class. It uses the `pypdf` library (`PdfReader`) to parse PDF files page-by-page, generating individual [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L6) objects for each non-empty page while capturing precise page metadata for granular source citations.

---

## Class Definition & Guidelines

### 1. Class Inheritance ([pdf_loader.py:L10](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L10))

`PDFLoader` inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L20) and implements `load(file_path: Path, file_hash: str) -> List[RawDocument]`.

### 2. PDF Reader Initialization ([pdf_loader.py:L15](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L15))

Opens and parses the binary structure of the target PDF file using `PdfReader(file_path)`.

### 3. Page-by-Page Extraction ([pdf_loader.py:L16-L28](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L16-L28))

- **Iteration**: Loops over `reader.pages` using `enumerate(..., idx)`.
- **Text Extraction**: Extracts text via `page.extract_text() or ""`, stripping surrounding whitespace ([pdf_loader.py:L17-L18](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L17-L18)).
- **Per-Page Metadata**: If non-empty text exists, builds metadata ([pdf_loader.py:L20-L27](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L20-L27)):
  - `source_file`: Absolute resolved path string.
  - `file_name`: File basename (e.g., `Q3_Report.pdf`).
  - `file_type`: `".pdf"`.
  - `file_hash`: SHA-256 string for incremental tracking.
  - `page_or_section`: `f"Page {idx + 1}"` (1-indexed page label).
  - `total_pages`: Total page count (`len(reader.pages)`).
- **Document List**: Appends a distinct [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L6) per page.

### 4. Logging & Error Handling ([pdf_loader.py:L29-L32](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L29-L32))

- Logs the number of successfully loaded pages (`logger.info`).
- Catches extraction exceptions, logs the error details (`logger.error`), and re-raises the exception.
