# Loader Factory Guidelines (`factory.py`)

## Folder & File Context

The [`src/loaders/factory/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory) directory contains [`factory.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py), which implements the Factory Pattern via [`LoaderFactory`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L16-L41).

It acts as a single point of dispatch for instantiating the appropriate loader based on a target file's extension.

---

## Detailed Code Explanation & Method Breakdown

### 1. Custom Exception ([`UnsupportedFormatError`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L10-L13))
- Exception subclass raised when encountering unregistered file extensions.

### 2. Loader Registry ([`LoaderFactory._LOADERS`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L19-L27))

| File Extension | Loader Class | Implementation Module |
| :--- | :--- | :--- |
| `.pdf` | [`PDFLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L13-L38) | [`src.loaders.pdf_loader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py) |
| `.docx` | [`DocxLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L13-L49) | [`src.loaders.docx_loader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py) |
| `.xlsx`, `.xls`, `.csv` | [`ExcelCSVLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L13-L56) | [`src.loaders.excel_loader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py) |
| `.txt`, `.md` | [`TextLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L12-L36) | [`src.loaders.text_loader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py) |

---

### 3. Factory Class Methods

- [`LoaderFactory.get_loader(file_path: Path) -> BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L29-L37):
  Checks `file_path.suffix.lower()`, retrieves corresponding loader class from `_LOADERS`, and instantiates it. Raises [`UnsupportedFormatError`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L10-L13) if unregistered.
- [`LoaderFactory.is_supported(file_path: Path) -> bool`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L39-L41):
  Returns `True` if file suffix is present in `_LOADERS`.
