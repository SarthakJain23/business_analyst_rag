# 📄 Guideline: `src/loaders/factory/factory.py` — Loader Factory

> **File**: [`factory.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py)
> **Lines**: 42 | **Role**: Maps file extensions to concrete loader classes
> **Module**: `src.loaders.factory`

---

## 1. High-Level Overview

### Purpose
`LoaderFactory` implements the **Factory Pattern** to instantiate the correct document loader based on a file's extension. It decouples the ingestion engine from knowing which loader handles which file type.

### Architectural Role
The factory sits at the entry point of the loading subsystem. `IngestionEngine` calls `LoaderFactory.get_loader(file_path)` and receives a `BaseLoader` instance ready to call `.load()`. Adding a new file format requires only:
1. Implementing a new loader class
2. Adding a mapping to `_LOADERS`

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Factory Pattern** | Class-level `get_loader()` method maps extensions to loader classes |
| **Registry Pattern** | `_LOADERS` dict is a static registry of extension → loader class mappings |
| **Open/Closed Principle** | New formats can be added without modifying existing loaders or the ingestion engine |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `pathlib.Path` | File path handling |
| `src.loaders.base.base.BaseLoader` | Abstract interface (return type) |
| `src.loaders.docx_loader.docx_loader.DocxLoader` | `.docx` handler |
| `src.loaders.excel_loader.excel_loader.ExcelCSVLoader` | `.xlsx`, `.xls`, `.csv` handler |
| `src.loaders.pdf_loader.pdf_loader.PDFLoader` | `.pdf` handler |
| `src.loaders.text_loader.text_loader.TextLoader` | `.txt`, `.md` handler |

---

## 3. Low-Level Breakdown

### 3.1 `UnsupportedFormatError` (Lines 10–13)
```python
class UnsupportedFormatError(Exception):
    """Raised when an unsupported file format is encountered."""
    pass
```
Custom exception for unsupported file types. Inherits from `Exception` (not `ValueError`) to allow specific catching.

### 3.2 `LoaderFactory._LOADERS` Registry (Lines 19–27)
```python
_LOADERS = {
    ".pdf": PDFLoader,
    ".docx": DocxLoader,
    ".xlsx": ExcelCSVLoader,
    ".xls": ExcelCSVLoader,
    ".csv": ExcelCSVLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
}
```

| Extension | Loader Class | Notes |
|-----------|-------------|-------|
| `.pdf` | `PDFLoader` | Single loader |
| `.docx` | `DocxLoader` | Single loader |
| `.xlsx` | `ExcelCSVLoader` | Shared loader for all tabular data |
| `.xls` | `ExcelCSVLoader` | Legacy Excel format |
| `.csv` | `ExcelCSVLoader` | Also tabular |
| `.txt` | `TextLoader` | Shared loader for plain text |
| `.md` | `TextLoader` | Markdown treated as plain text |

### 3.3 `get_loader()` Class Method (Lines 29–37)
```python
@classmethod
def get_loader(cls, file_path: Path) -> BaseLoader:
    ext = file_path.suffix.lower()
    loader_cls = cls._LOADERS.get(ext)
    if not loader_cls:
        raise UnsupportedFormatError(
            f"Unsupported file extension '{ext}' for file {file_path.name}"
        )
    return loader_cls()
```
1. Extracts lowercase extension from path
2. Looks up in `_LOADERS` registry
3. Raises `UnsupportedFormatError` if not found
4. **Instantiates a new loader** each time (stateless — no caching needed)

### 3.4 `is_supported()` Class Method (Lines 39–41)
```python
@classmethod
def is_supported(cls, file_path: Path) -> bool:
    return file_path.suffix.lower() in cls._LOADERS
```
Pre-check method used by `IngestionEngine` to skip unsupported files without raising exceptions.

---

## 4. Data Flow

```
file_path.suffix → _LOADERS[ext] → LoaderClass() → BaseLoader instance
```

### Usage in IngestionEngine
```python
if not LoaderFactory.is_supported(file_path):
    continue  # skip

loader = LoaderFactory.get_loader(file_path)
documents = loader.load(file_path, file_hash)
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Dynamic Registration** | Adding formats requires modifying `_LOADERS` directly | Add a `register(ext, loader_cls)` class method for plugin-style registration |
| **Singleton Loaders** | New loader instance created on every `get_loader()` call | Cache loader instances (they're stateless, so a single instance per type suffices) |
| **MIME Type Support** | Only extension-based detection; renamed files would fail | Add optional MIME type detection fallback (e.g., `python-magic`) |
| **Case Sensitivity** | `.PDF` and `.pdf` both work (lowercase conversion) | Already handled ✅ |
| **Missing Formats** | No support for HTML, JSON, XML, Markdown-with-YAML, PowerPoint | Add loaders for additional business document formats |
