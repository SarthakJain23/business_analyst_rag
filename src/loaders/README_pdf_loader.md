# Code Explanation: `pdf_loader.py`

## Overview
The [`pdf_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py) module defines the `PDFLoader` class. It uses the `pypdf` library (`PdfReader`) to parse PDF files page-by-page, generating individual [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L8) objects for each non-empty page while capturing precise page metadata for granular source citations.

---

## Class Definition & Code Flow

### 1. Class Inheritance ([pdf_loader.py:L12](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py#L12))
`PDFLoader` inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L23) and implements `load(file_path: Path, file_hash: str) -> List[RawDocument]`.

### 2. PDF Reader Initialization ([pdf_loader.py:L18](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py#L18))
Opens and parses the binary structure of the target PDF file using `PdfReader(file_path)`.

### 3. Page-by-Page Extraction ([pdf_loader.py:L19-L31](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py#L19-L31))
- **Iteration**: Loops over `reader.pages` using `enumerate(..., idx)`.
- **Text Extraction**: Extracts text via `page.extract_text() or ""`, stripping surrounding whitespace ([pdf_loader.py:L20-L21](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py#L20-L21)).
- **Per-Page Metadata**: If non-empty text exists, builds metadata ([pdf_loader.py:L23-L30](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py#L23-L30)):
  - `source_file`: Absolute resolved path string.
  - `file_name`: File basename (e.g., `Q3_Report.pdf`).
  - `file_type`: `".pdf"`.
  - `file_hash`: SHA-256 string for incremental tracking.
  - `page_or_section`: `f"Page {idx + 1}"` (1-indexed page label).
  - `total_pages`: Total page count (`len(reader.pages)`).
- **Document List**: Appends a distinct [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L8) per page.

### 4. Logging & Error Handling ([pdf_loader.py:L32-L35](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py#L32-L35))
- Logs the number of successfully loaded pages (`logger.info`).
- Catches extraction exceptions, logs the error details (`logger.error`), and re-raises the exception.
