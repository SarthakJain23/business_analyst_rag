# 📄 Guideline: `src/loaders/pdf_loader/pdf_loader.py` — PDF Document Loader

> **File**: [`pdf_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py)
> **Lines**: 39 | **Role**: Loads `.pdf` files into LangChain Documents (one per page)
> **Module**: `src.loaders.pdf_loader`

---

## 1. High-Level Overview

### Purpose
`PDFLoader` extracts text from PDF files using `pypdf`, creating a **separate `Document` per page**. This preserves page-level metadata boundaries, which is important for citation accuracy (e.g., "Source: report.pdf, Page 3").

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Strategy** | Concrete implementation of `BaseLoader` for `.pdf` files |
| **Per-Unit Processing** | One `Document` per page (unlike DOCX which produces one for the entire file) |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `pypdf.PdfReader` | PDF parsing library (pure Python, no external deps) |
| `langchain_core.documents.Document` | LangChain document data structure |
| `src.loaders.base.base.BaseLoader` | Abstract interface |
| `src.utils.logger` | Logging |

---

## 3. Low-Level Breakdown

### 3.1 `PDFLoader.load()` Method (Lines 16–38)

```python
def load(self, file_path: Path, file_hash: str) -> List[Document]:
```

#### Step 1: Open & Parse PDF (Line 19)
```python
reader = PdfReader(file_path)
```
- `pypdf.PdfReader` accepts `Path` objects directly
- Parses the PDF structure (pages, fonts, etc.)

#### Step 2: Extract Text Per Page (Lines 20–32)
```python
for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    text = text.strip()
    if text:
        metadata = {
            "source_file": str(file_path.resolve()),
            "file_name": file_path.name,
            "file_type": ".pdf",
            "file_hash": file_hash,
            "page_or_section": f"Page {idx + 1}",
            "total_pages": len(reader.pages),
        }
        documents.append(Document(page_content=text, metadata=metadata))
```

Per page:
1. Calls `page.extract_text()` (returns `None` if extraction fails)
2. Falls back to empty string on `None`
3. Strips whitespace
4. Skips pages with no extractable text (e.g., images-only pages)
5. Creates `Document` with page-specific metadata

**Unique metadata fields**:
- `page_or_section`: `"Page 1"`, `"Page 2"`, etc. (1-indexed for human readability)
- `total_pages`: Total page count from the PDF

#### Step 3: Logging (Line 33)
```python
logger.info(f"Successfully loaded {len(documents)} pages from PDF: {file_path.name}")
```
Reports how many pages had extractable text (may be less than `total_pages`).

---

## 4. Data Flow

```
.pdf file
    │
    ▼
PdfReader(file_path)
    │
    ├── Page 1 → extract_text() → Document(page_content=..., metadata={page_or_section: "Page 1"})
    ├── Page 2 → extract_text() → Document(page_content=..., metadata={page_or_section: "Page 2"})
    ├── Page 3 → (image only, empty) → SKIPPED
    └── Page 4 → extract_text() → Document(page_content=..., metadata={page_or_section: "Page 4"})
    │
    ▼
List[Document]  (3 documents for a 4-page PDF with one image-only page)
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **OCR Support** | Image-only pages are silently skipped | Integrate OCR (e.g., `pytesseract`) for scanned PDFs |
| **Table Extraction** | Tables are extracted as raw text (loses structure) | Use `pypdf` table extraction or `camelot-py` for structured table parsing |
| **Metadata** | No extraction of PDF metadata (author, title, creation date) | Add `reader.metadata` fields to document metadata |
| **Layout Awareness** | Multi-column PDFs may produce jumbled text | Consider `pdfplumber` or `unstructured` for layout-aware extraction |
| **Password Protection** | Encrypted PDFs will throw an error | Add `password` parameter or graceful handling with informative error |
| **Performance** | Small pages create many Documents that get further split by TextSplitter | Optionally merge short consecutive pages before chunking |
