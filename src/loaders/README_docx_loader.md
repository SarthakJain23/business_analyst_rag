# Code Explanation: `docx_loader.py`

## Overview
The [`docx_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py) module provides the `DocxLoader` class for ingesting Microsoft Word (`.docx`) files. It extracts text paragraphs and converts embedded Word tables into Markdown format.

## Class Definition
`DocxLoader` inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L23) and implements `load(file_path: Path, file_hash: str) -> List[RawDocument]`.

---

## Detailed Code Flow

### 1. Document Loading
- Opens file using `docx.Document(str(file_path))` ([docx_loader.py:L18](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L18)).

### 2. Paragraph Parsing
- Iterates over `doc.paragraphs` ([docx_loader.py:L22](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L22)).
- Strips whitespace and appends non-empty text strings to `full_text`.

### 3. Table Formatting
- Iterates over `doc.tables` ([docx_loader.py:L26](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L26)).
- Converts rows into Markdown table syntax (`| Cell 1 | Cell 2 |`) ([docx_loader.py:L30](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L30)).
- Replaces internal cell newlines with spaces to avoid breaking table layout.

### 4. RawDocument Creation & Metadata
- Combines content using double newlines (`\n\n`) ([docx_loader.py:L33](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L33)).
- Constructs metadata: `source_file`, `file_name`, `file_type`, `file_hash`, and `page_or_section: "Document Body"` ([docx_loader.py:L35-L41](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L35-L41)).
- Returns [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L8) object.

### 5. Logging & Error Handling
- Logs success or handles exceptions and re-raises ([docx_loader.py:L44-L47](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py#L44-L47)).
