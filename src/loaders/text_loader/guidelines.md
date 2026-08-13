# Text & Markdown Loader Guidelines (`text_loader.py`)

## Folder & File Context

The [`src/loaders/text_loader/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader) directory contains [`text_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py), which defines [`TextLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L12-L36).

It parses plain text (`.txt`) and Markdown (`.md`) documents with resilient UTF-8 decoding.

---

## Detailed Code Explanation & Method Breakdown

### Class: [`TextLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L12-L36)

- **Inheritance**: Inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14).
- **Method**: [`load(file_path: Path, file_hash: str) -> List[Document]`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L15-L36):
  1. Reads file using `open(file_path, "r", encoding="utf-8", errors="replace")` ([L18](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L18)). `errors="replace"` prevents character decoding crashes.
  2. Strips surrounding whitespace via `.strip()` ([L19](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L19)).
  3. Constructs `Document` with metadata (`source_file`, `file_name`, `file_type: file_path.suffix.lower()`, `file_hash`, `page_or_section: "Document Content"`) ([L22-L29](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L22-L29)).
