# Document Loaders Module - Guidelines

## Purpose

The `src/loaders/` module is responsible for ingesting files from `data/documents/` and parsing them into standardized `RawDocument` objects containing raw text content and rich metadata. Each loader lives in its own dedicated subfolder alongside its implementation guidelines.

## Directory Structure

```
src/loaders/
├── base/
│   ├── __init__.py
│   ├── base.py
│   └── guidelines.md
├── docx_loader/
│   ├── __init__.py
│   ├── docx_loader.py
│   └── guidelines.md
├── excel_loader/
│   ├── __init__.py
│   ├── excel_loader.py
│   └── guidelines.md
├── factory/
│   ├── __init__.py
│   ├── factory.py
│   └── guidelines.md
├── pdf_loader/
│   ├── __init__.py
│   ├── pdf_loader.py
│   └── guidelines.md
├── text_loader/
│   ├── __init__.py
│   ├── text_loader.py
│   └── guidelines.md
├── __init__.py
├── README.md
└── guidelines.md
```

## Loader Guidelines Index

- 📐 [Base Loader Guidelines (`src/loaders/base/guidelines.md`)](base/guidelines.md) — Standardized `BaseLoader` & `RawDocument` interface specifications.
- 🏭 [Loader Factory Guidelines (`src/loaders/factory/guidelines.md`)](factory/guidelines.md) — Factory pattern implementation & dispatch registry.
- 📕 [PDF Loader Guidelines (`src/loaders/pdf_loader/guidelines.md`)](pdf_loader/guidelines.md) — PDF extraction, page metadata, and citations.
- 📄 [Excel & CSV Loader Guidelines (`src/loaders/excel_loader/guidelines.md`)](excel_loader/guidelines.md) — Workbooks, sheets, and Markdown tabular conversions.
- 📄 [Word Document Loader Guidelines (`src/loaders/docx_loader/guidelines.md`)](docx_loader/guidelines.md) — Paragraph extraction and table layout parsing.
- 📝 [Text & Markdown Loader Guidelines (`src/loaders/text_loader/guidelines.md`)](text_loader/guidelines.md) — Plain text and Markdown file parsing.
