# Document Loaders Module - Guidelines

## Purpose
The `src/loaders/` module is responsible for ingesting files from `data/documents/` and parsing them into standardized `Document` objects containing raw text content and rich metadata.

## Structural Design & Patterns
1. **Abstract Interface (`base.py`)**:
   - All parser implementations MUST inherit from `BaseLoader`.
   - `BaseLoader` defines the contract `load(file_path: Path) -> List[Document]`.
   - Every `Document` output MUST include essential metadata fields:
     - `source_file`: Absolute path of the document.
     - `file_name`: Basename of the file.
     - `file_type`: Format extension (e.g., `.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.md`).
     - `file_hash`: SHA-256 hash of the file.
     - `page_or_section`: Page number, sheet name, or section identifier where available.

2. **Loader Factory (`factory.py`)**:
   - Uses the Factory Pattern to route file paths to the appropriate loader instance based on extension. See [README_factory.md](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_factory.md).
   - Raises an explicit `UnsupportedFormatError` if an unsupported format is encountered.

3. **Format Specific Guidelines**:
   - **PDF (`pdf_loader.py`)**: Preserves page numbers in metadata for precise source citation. See [README_pdf_loader.md](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_pdf_loader.md).
   - **Word (`docx_loader.py`)**: Extracts body text paragraphs and converts embedded tables into readable text blocks. See [README_docx_loader.md](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_docx_loader.md).
   - **Excel & CSV (`excel_loader.py`)**: Converts workbooks and tables into Markdown table syntax (`| Header | ... |`) so LLM can interpret row-column relationships accurately. See [README_excel_loader.md](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_excel_loader.md).
   - **Text & Markdown (`text_loader.py`)**: Reads plain text/markdown while maintaining structural headers. See [README_text_loader.md](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_text_loader.md).

---

## Detailed Code Explanation Index
- 🏭 [Loader Factory Explanation (`README_factory.md`)](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_factory.md) - Full walkthrough of `factory.py`.
- 📕 [PDF Loader Explanation (`README_pdf_loader.md`)](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_pdf_loader.md) - Full walkthrough of `pdf_loader.py`.
- 📄 [Excel & CSV Loader Explanation (`README_excel_loader.md`)](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_excel_loader.md) - Full walkthrough of `excel_loader.py`.
- 📄 [Word Document Loader Explanation (`README_docx_loader.md`)](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_docx_loader.md) - Full walkthrough of `docx_loader.py`.
- 📝 [Text & Markdown Loader Explanation (`README_text_loader.md`)](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_text_loader.md) - Full walkthrough of `text_loader.py`.






