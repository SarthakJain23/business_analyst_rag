# 📄 Guideline: `src/loaders/text_loader/text_loader.py` — Plain Text / Markdown Loader

> **File**: [`text_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py)
> **Lines**: 37 | **Role**: Loads `.txt` and `.md` files into LangChain Documents
> **Module**: `src.loaders.text_loader`

---

## 1. High-Level Overview

### Purpose
`TextLoader` is the simplest loader — it reads the entire file as a single string and wraps it in a LangChain `Document`. It handles both `.txt` (plain text) and `.md` (Markdown) files identically.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Strategy** | Concrete implementation of `BaseLoader` for text files |
| **Simplest Implementation** | Minimal transformation; content is preserved as-is |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `langchain_core.documents.Document` | LangChain document data structure |
| `src.loaders.base.base.BaseLoader` | Abstract interface |
| `src.utils.logger` | Logging |

---

## 3. Low-Level Breakdown

### 3.1 `TextLoader.load()` Method (Lines 15–36)

```python
def load(self, file_path: Path, file_hash: str) -> List[Document]:
```

#### Step 1: Read File (Lines 18–19)
```python
with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read().strip()
```
- Opens with **explicit UTF-8 encoding**
- `errors="replace"` replaces invalid bytes with `�` instead of crashing — important for files with mixed encodings
- Reads entire file into memory
- Strips leading/trailing whitespace

#### Step 2: Create Document (Lines 21–29)
```python
if content:
    metadata = {
        "source_file": str(file_path.resolve()),
        "file_name": file_path.name,
        "file_type": file_path.suffix.lower(),
        "file_hash": file_hash,
        "page_or_section": "Document Content",
    }
    documents.append(Document(page_content=content, metadata=metadata))
```
- Only creates a `Document` if content is non-empty
- `file_type` dynamically set from suffix (`.txt` or `.md`)
- `page_or_section` is a static `"Document Content"` (no internal sectioning)
- Returns a **single Document** for the entire file (chunking is done later by `TextSplitter`)

---

## 4. Data Flow

```
.txt / .md file
      │
      ▼
open(encoding="utf-8", errors="replace")
      │
      ▼
f.read().strip()
      │
      ├── empty → return []
      │
      └── non-empty → Document(
                         page_content=<entire file content>,
                         metadata={page_or_section: "Document Content"}
                       )
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Markdown Awareness** | `.md` files are treated as plain text with no structural parsing | Parse markdown headings to create per-section Documents |
| **Encoding Detection** | Assumes UTF-8; `errors="replace"` masks encoding issues silently | Use `chardet` for encoding detection, or at least log when replacement occurs |
| **Large Files** | Reads entire file into memory | For very large text files, consider streaming or chunked reading |
| **Front Matter** | Markdown YAML front matter is included as regular content | Strip or parse YAML front matter (e.g., using `python-frontmatter`) |
| **Line Endings** | No normalization of line endings (CRLF vs LF) | Normalize to LF for consistent chunking behavior |
