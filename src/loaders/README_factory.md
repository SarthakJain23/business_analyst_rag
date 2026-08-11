# Code Explanation: `factory.py`

## Overview
The [`factory.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory.py) module implements the Factory Pattern via the `LoaderFactory` class. It acts as a single point of dispatch for instantiating the appropriate document loader ([`PDFLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py), [`DocxLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py), [`ExcelCSVLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py), or [`TextLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader.py)) based on a given file's extension.

---

## Key Classes & Code Flow

### 1. `UnsupportedFormatError` Exception ([factory.py:L10](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory.py#L10))
Custom exception subclass of `Exception` raised when an unsupported file format or extension is passed to the factory.

### 2. `LoaderFactory` Registry (`_LOADERS`) ([factory.py:L19-L27](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory.py#L19-L27))
Internal class dictionary mapping file extension strings (lowercase) to loader classes:

| Extension | Loader Class |
| :--- | :--- |
| `.pdf` | `PDFLoader` |
| `.docx` | `DocxLoader` |
| `.xlsx`, `.xls`, `.csv` | `ExcelCSVLoader` |
| `.txt`, `.md` | `TextLoader` |

### 3. Factory Method: `get_loader` ([factory.py:L29-L37](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory.py#L29-L37))
```python
@classmethod
def get_loader(cls, file_path: Path) -> BaseLoader:
    ext = file_path.suffix.lower()
    loader_cls = cls._LOADERS.get(ext)
    if not loader_cls:
        raise UnsupportedFormatError(f"Unsupported file extension '{ext}' for file {file_path.name}")
    return loader_cls()
```
- Extracts file extension using `file_path.suffix.lower()`.
- Looks up the corresponding loader class in `_LOADERS`.
- Instantiates and returns the loader object, or raises `UnsupportedFormatError` if missing.

### 4. Utility Method: `is_supported` ([factory.py:L39-L41](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory.py#L39-L41))
```python
@classmethod
def is_supported(cls, file_path: Path) -> bool:
    return file_path.suffix.lower() in cls._LOADERS
```
Checks if a file extension is registered in the factory registry without throwing an exception.
