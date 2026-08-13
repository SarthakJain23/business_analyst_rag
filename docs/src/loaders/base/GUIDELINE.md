# 📄 Guideline: `src/loaders/base/base.py` — Abstract Loader Interface

> **File**: [`base.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py)
> **Lines**: 15 | **Role**: Defines the abstract base class for all document loaders
> **Module**: `src.loaders.base`

---

## 1. High-Level Overview

### Purpose
`base.py` defines the `BaseLoader` **abstract base class** (ABC) that all concrete document loaders must implement. It enforces a consistent interface: every loader must have a `load()` method that takes a file path and hash, and returns a list of LangChain `Document` objects.

### Architectural Role
This is the **contract definition** for the loader subsystem. The `LoaderFactory` returns `BaseLoader` instances, and the `IngestionEngine` calls `.load()` without knowing which concrete loader is being used.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Template Method / Abstract Interface** | `BaseLoader` defines the method signature; subclasses provide implementation |
| **Strategy Pattern** | Different loaders are interchangeable strategies for loading different file types |
| **Liskov Substitution Principle** | All loaders can be used anywhere a `BaseLoader` is expected |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `abc.ABC, abstractmethod` | Python abstract base class machinery |
| `pathlib.Path` | Cross-platform file paths |
| `typing.List` | Type annotation |
| `langchain_core.documents.Document` | LangChain document data structure |

---

## 3. Low-Level Breakdown

### 3.1 `BaseLoader` Class (Lines 8–14)
```python
class BaseLoader(ABC):
    """Abstract Base Class for all document loaders returning LangChain Documents."""

    @abstractmethod
    def load(self, file_path: Path, file_hash: str) -> List[Document]:
        """Loads and parses a file into a list of LangChain Document instances."""
        pass
```

#### Method Contract: `load(file_path, file_hash)`

| Parameter | Type | Purpose |
|-----------|------|---------|
| `file_path` | `Path` | Absolute path to the file on disk |
| `file_hash` | `str` | SHA-256 hash of the file (for metadata tagging) |
| **Returns** | `List[Document]` | One or more LangChain Documents with `page_content` and `metadata` |

#### Metadata Contract (implicit)
All concrete loaders are expected to include these metadata fields in each returned `Document`:

| Metadata Key | Type | Description |
|-------------|------|-------------|
| `source_file` | `str` | Absolute file path (resolved) |
| `file_name` | `str` | File basename (e.g., `"report.pdf"`) |
| `file_type` | `str` | File extension (e.g., `".pdf"`) |
| `file_hash` | `str` | SHA-256 hash passed as argument |
| `page_or_section` | `str` | Location within file (e.g., `"Page 3"`, `"Sheet: Revenue"`) |

---

## 4. Concrete Implementations

| Loader | File Types | Module |
|--------|-----------|--------|
| `PDFLoader` | `.pdf` | `src.loaders.pdf_loader` |
| `DocxLoader` | `.docx` | `src.loaders.docx_loader` |
| `ExcelCSVLoader` | `.xlsx`, `.xls`, `.csv` | `src.loaders.excel_loader` |
| `TextLoader` | `.txt`, `.md` | `src.loaders.text_loader` |

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Async Support** | No async `load()` method | Add `async def aload()` for async I/O support |
| **Metadata Enforcement** | Metadata contract is implicit (not validated) | Define a `LoaderMetadata` TypedDict and validate in a base `load()` wrapper |
| **Error Contract** | No defined error handling contract | Document expected exceptions (e.g., `FileNotFoundError`, `PermissionError`) |
| **Streaming Support** | No support for streaming large files | Add optional `load_chunks()` generator method for very large files |
