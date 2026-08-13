# PDF Loader Guidelines (`pdf_loader.py`)

## Folder & File Context

The [`src/loaders/pdf_loader/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader) directory contains [`pdf_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py), which defines [`PDFLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L13-L38).

It uses `pypdf.PdfReader` to extract text from PDF files page-by-page, attaching detailed 1-indexed page metadata to enable granular source citation rendering in the UI.

---

## Detailed Code Explanation & Class Breakdown

### Class: [`PDFLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L13-L38)

- **Inheritance**: Inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14).
- **Method**: [`load(file_path: Path, file_hash: str) -> List[Document]`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L16-L38):
  1. Opens PDF using `PdfReader(file_path)` ([L19](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L19)).
  2. Loops over `reader.pages` using `enumerate(..., start=0)` ([L20](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L20)).
  3. Extracts page text via `page.extract_text()` ([L21](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L21)).
  4. Skips empty pages and creates `Document` with metadata (`source_file`, `file_name`, `file_type: ".pdf"`, `file_hash`, `page_or_section: f"Page {idx + 1}"`, `total_pages`) ([L24-L32](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L24-L32)).
  5. Catches and logs exceptions via `logger.error` before re-raising ([L34-L36](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L34-L36)).
