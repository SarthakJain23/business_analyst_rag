# Document Loaders Module (`src/loaders`)

The `src/loaders/` package provides modular file parsers for business documents. Each loader is isolated in its own subfolder containing its Python implementation, `__init__.py`, and dedicated `guidelines.md`.

## Loaders Subfolder Index

- 📐 **Base Loader**: [`src/loaders/base/base.py`](base/base.py) — See [`guidelines.md`](base/guidelines.md)
- 🏭 **Loader Factory**: [`src/loaders/factory/factory.py`](factory/factory.py) — See [`guidelines.md`](factory/guidelines.md)
- 📕 **PDF Loader**: [`src/loaders/pdf_loader/pdf_loader.py`](pdf_loader/pdf_loader.py) — See [`guidelines.md`](pdf_loader/guidelines.md)
- 📊 **Excel & CSV Loader**: [`src/loaders/excel_loader/excel_loader.py`](excel_loader/excel_loader.py) — See [`guidelines.md`](excel_loader/guidelines.md)
- 📝 **Word Document Loader**: [`src/loaders/docx_loader/docx_loader.py`](docx_loader/docx_loader.py) — See [`guidelines.md`](docx_loader/guidelines.md)
- 📄 **Text & Markdown Loader**: [`src/loaders/text_loader/text_loader.py`](text_loader/text_loader.py) — See [`guidelines.md`](text_loader/guidelines.md)

For overall module architecture, see [`guidelines.md`](guidelines.md).
