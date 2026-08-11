# Document Loaders Module (`src/loaders`)

This directory contains file format extractors for the Business Analyst RAG application.

## Loader Architecture
All document loaders inherit from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L23) and output standardized [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L8) dataclass objects containing formatted text and rich metadata.

## Available Loaders & Code Explanations
- 📊 **Excel & CSV Loader**: [`excel_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py) — Read detailed explanation in [`README_excel_loader.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_excel_loader.md).
- 📝 **Word Document Loader**: [`docx_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/docx_loader.py) — Read detailed explanation in [`README_docx_loader.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_docx_loader.md).
- 📕 **PDF Loader**: [`pdf_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/pdf_loader.py) — Read detailed explanation in [`README_pdf_loader.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_pdf_loader.md).
- 📄 **Text & Markdown Loader**: [`text_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/text_loader.py) — Read detailed explanation in [`README_text_loader.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_text_loader.md).
- 🏭 **Loader Factory**: [`factory.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/factory.py) — Read detailed explanation in [`README_factory.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/README_factory.md).

For module guidelines, see [`guidelines.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/guidelines.md).

