# Word Document Loader Guidelines (`docx_loader.py`)

## Folder & File Context

The [`src/loaders/docx_loader/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader) directory contains [`docx_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py), which defines [`DocxLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L13-L49).

It processes Microsoft Word (`.docx`) files using `python-docx`, extracting paragraph text and converting embedded Word tables into Markdown format tables.

---

## Detailed Code Explanation & Class Breakdown

### Class: [`DocxLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L13-L49)

- **Inheritance**: Inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14).
- **Method**: [`load(file_path: Path, file_hash: str) -> List[Document]`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L16-L49):
  1. Opens document via `docx.Document(str(file_path))` ([L19](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L19)).
  2. Iterates over `doc.paragraphs`, adding non-empty text strings ([L22-L24](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L22-L24)).
  3. Iterates over `doc.tables`, formatting rows into Markdown table syntax (`| Cell 1 | Cell 2 |`) ([L26-L31](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L26-L31)). Replaces internal cell newlines with spaces to avoid breaking table layout.
  4. Combines text with double newlines (`\n\n`) and constructs metadata (`source_file`, `file_name`, `file_type: ".docx"`, `file_hash`, `page_or_section: "Document Body"`) ([L33-L42](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L33-L42)).
