# 📄 Guideline: `src/loaders/docx_loader/docx_loader.py` — Word Document Loader

> **File**: [`docx_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py)
> **Lines**: 50 | **Role**: Loads `.docx` files into LangChain Documents
> **Module**: `src.loaders.docx_loader`

---

## 1. High-Level Overview

### Purpose
`DocxLoader` extracts text content from Microsoft Word `.docx` files, including both **paragraph text** and **table data** (formatted as markdown). It produces a single `Document` containing all content from the file.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Strategy** | Concrete implementation of `BaseLoader` for `.docx` files |
| **Adapter** | Adapts `python-docx` library output to LangChain `Document` format |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `docx` (`python-docx`) | Microsoft Word document parser |
| `langchain_core.documents.Document` | LangChain document data structure |
| `src.loaders.base.base.BaseLoader` | Abstract interface |
| `src.utils.logger` | Logging |

---

## 3. Low-Level Breakdown

### 3.1 `DocxLoader.load()` Method (Lines 16–49)

#### Step 1: Parse Document (Line 19)
```python
doc = docx.Document(str(file_path))
```
- Wraps `Path` to `str` (python-docx requires string path)

#### Step 2: Extract Paragraphs (Lines 22–24)
```python
for p in doc.paragraphs:
    if p.text.strip():
        full_text.append(p.text.strip())
```
- Iterates all paragraphs in the document
- Skips empty paragraphs (whitespace-only)
- Strips leading/trailing whitespace

#### Step 3: Extract Tables (Lines 26–31)
```python
for table_idx, table in enumerate(doc.tables):
    table_lines = [f"\n### Table {table_idx + 1}"]
    for row in table.rows:
        row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
        table_lines.append("| " + " | ".join(row_cells) + " |")
    full_text.append("\n".join(table_lines))
```
- Tables are converted to **markdown pipe table** format
- Each table gets a `### Table N` header
- Cell newlines are replaced with spaces to prevent table format breaking
- **Note**: No header row separator (`|---|---|`) is generated — this is technically invalid markdown

#### Step 4: Combine & Create Document (Lines 33–42)
```python
combined_content = "\n\n".join(full_text)
```
- Joins all paragraphs and tables with double newlines
- Only creates a `Document` if content is non-empty
- Sets `page_or_section` to `"Document Body"` (single section for entire document)

---

## 4. Data Flow

```
.docx file
    │
    ├── python-docx parser
    │       ├── doc.paragraphs → stripped text
    │       └── doc.tables → markdown pipe tables
    │
    ▼
Single Document(page_content="...", metadata={...})
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Table Format** | Missing header separator in markdown tables | Add `|---|---|` after the first row |
| **Section Awareness** | Entire document is one chunk; no heading-based sectioning | Split by heading styles (e.g., `p.style.name.startswith('Heading')`) |
| **Images** | Inline images are silently dropped | Log a warning when images are detected |
| **Styles** | Bold, italic, and other formatting is lost | Preserve formatting as markdown (e.g., `**bold**`, `*italic*`) |
| **Large Documents** | Returns one document even for very large files | Split into per-section documents based on heading hierarchy |
