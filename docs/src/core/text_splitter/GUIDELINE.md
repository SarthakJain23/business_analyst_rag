# 📄 Guideline: `src/core/text_splitter/text_splitter.py` — Document Chunking Engine

> **File**: [`text_splitter.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/text_splitter/text_splitter.py)
> **Lines**: 45 | **Role**: Splits documents into vector-ready chunks with metadata
> **Module**: `src.core.text_splitter`

---

## 1. High-Level Overview

### Purpose
The `TextSplitter` takes a list of LangChain `Document` objects (raw loaded documents) and splits them into smaller, overlapping chunks suitable for embedding and vector storage. It enriches each chunk with a **deterministic `chunk_id`** and positional metadata.

### Architectural Role
This module sits between the **loaders** (which produce full documents) and the **vector store** (which needs small, embeddable chunks). It is called by the `IngestionEngine` during the ingestion pipeline.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Adapter/Wrapper** | Wraps LangChain's `RecursiveCharacterTextSplitter` with custom metadata enrichment logic |
| **Decorator Pattern** (data) | Adds `chunk_id`, `chunk_index`, and `total_chunks` metadata to each split document |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `langchain_core.documents.Document` | LangChain's document data structure |
| `langchain_text_splitters.RecursiveCharacterTextSplitter` | The actual text splitting algorithm |
| `src.config.settings` | Default `CHUNK_SIZE` (1000) and `CHUNK_OVERLAP` (150) |

---

## 3. Low-Level Breakdown

### 3.1 `TextSplitter.__init__()` (Lines 12–21)
```python
def __init__(
    self, chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP
):
    self.splitter = RecursiveCharacterTextSplitter(
        chunk_size=self.chunk_size,
        chunk_overlap=self.chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
```

**Separator Hierarchy** (most to least preferred):
1. `"\n\n"` — Paragraph boundary (preserves semantic units)
2. `"\n"` — Line boundary
3. `" "` — Word boundary
4. `""` — Character boundary (last resort)

The splitter tries to split at the highest-priority separator that keeps chunks under `chunk_size`.

### 3.2 `split_documents()` Method (Lines 23–44)

```python
def split_documents(self, documents: List[Document]) -> List[Document]:
```

**Algorithm** (per input document):

1. **Split text**: `self.splitter.split_documents([doc])` → produces `N` chunk documents
2. **Generate chunk ID** (Lines 28–33):
   ```python
   file_hash = str(doc.metadata.get("file_hash", "nohash"))[:8]
   page_sec = doc.metadata.get("page_or_section", "sec")
   clean_sec = "".join(c for c in str(page_sec) if c.isalnum() or c in ("_", "-"))
   chunk_id = f"{file_hash}_{clean_sec}_chunk_{idx}"
   ```
   - Takes first 8 chars of file hash (for brevity)
   - Sanitizes `page_or_section` to alphanumeric + `_-` only
   - Produces IDs like: `a1b2c3d4_Page1_chunk_0`

3. **Enrich metadata** (Lines 34–41):
   ```python
   meta.update({
       "chunk_id": chunk_id,
       "chunk_index": idx,
       "total_chunks": len(splits),
   })
   ```
   - Preserves all original metadata from the source document
   - Adds three new fields for chunk identification and ordering

4. **Build output** (Line 42):
   ```python
   chunked_docs.append(Document(page_content=split_doc.page_content, metadata=meta))
   ```

**Key Design Choice**: Each input document is split independently, so a 5-page PDF produces 5 separate splitting operations (not one merged text). This preserves per-page metadata boundaries.

---

## 4. Data Flow

```
List[Document]  (from loaders, with file metadata)
       │
       ▼
  For each document:
       │
       ├── RecursiveCharacterTextSplitter.split_documents()
       │         │
       │         ▼
       │   N chunk Documents (text split, metadata inherited)
       │         │
       │         ▼
       │   Enrich with chunk_id, chunk_index, total_chunks
       │
       ▼
List[Document]  (chunked, with enriched metadata)
```

### Example Metadata (Input → Output)
**Input Document Metadata**:
```json
{
  "source_file": "/path/to/report.pdf",
  "file_name": "report.pdf",
  "file_type": ".pdf",
  "file_hash": "a1b2c3d4e5f6...",
  "page_or_section": "Page 3",
  "total_pages": 10
}
```

**Output Chunk Metadata** (for chunk 2 of 4):
```json
{
  "source_file": "/path/to/report.pdf",
  "file_name": "report.pdf",
  "file_type": ".pdf",
  "file_hash": "a1b2c3d4e5f6...",
  "page_or_section": "Page 3",
  "total_pages": 10,
  "chunk_id": "a1b2c3d4_Page3_chunk_2",
  "chunk_index": 2,
  "total_chunks": 4
}
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Chunk ID Determinism** | If the same content is re-split with different hash (re-upload), old chunks aren't evicted by ID | Include content hash in chunk_id, or rely solely on `source_file` metadata for eviction (which is currently done) |
| **Table-Aware Splitting** | Tables in markdown can be broken mid-row | Add a custom separator for markdown table row boundaries (`\|`) |
| **Overlap Strategy** | Fixed overlap of 150 chars may be too much for small chunks | Make overlap a percentage of chunk size (e.g., 15%) |
| **Empty Chunk Filtering** | Doesn't filter chunks that are only whitespace after splitting | Add `if split_doc.page_content.strip():` guard |
| **Token-Based Splitting** | Character-based splitting doesn't account for token boundaries | Consider `TokenTextSplitter` from LangChain for more predictable LLM context usage |
