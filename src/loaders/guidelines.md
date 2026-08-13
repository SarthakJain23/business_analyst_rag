# Document Loaders Module - Guidelines

## Folder & Module Context

The [`src/loaders/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders) directory houses file-parsing components for the Business Analyst RAG pipeline.

It transforms heterogenous source files stored in `data/documents/` (PDF, Word, Excel workbooks, CSV tables, text files, Markdown notes) into standardized LangChain `Document` objects containing extracted text content and rich source metadata.

---

## Directory Index & Sub-Guidelines

Click any link below to navigate to a loader-specific guideline:

- 📐 [**Base Loader Guidelines**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/guidelines.md) — Abstract class [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14) interface contract.
- 🏭 [**Loader Factory Guidelines**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/guidelines.md) — Factory class [`LoaderFactory`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory/factory.py#L16-L41) dispatch registry.
- 📕 [**PDF Loader Guidelines**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/guidelines.md) — [`PDFLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader/pdf_loader.py#L13-L38) page extraction and metadata.
- 📄 [**Excel & CSV Loader Guidelines**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/guidelines.md) — [`ExcelCSVLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L13-L56) tabular markdown conversion.
- 📄 [**Word Document Loader Guidelines**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/guidelines.md) — [`DocxLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader/docx_loader.py#L13-L49) paragraph & table parsing.
- 📝 [**Text & Markdown Loader Guidelines**](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/guidelines.md) — [`TextLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader/text_loader.py#L12-L36) UTF-8 text file parsing.
