# Core Ingestion Module (`src/core`)

The `src/core/` package orchestrates incremental document processing, hash-based change tracking, text chunking, and vector database synchronization. Each core engine component is isolated in its own subfolder containing its Python implementation, `__init__.py`, and dedicated `guidelines.md`.

## Core Subfolder Index

- ⚙️ **Ingestion Engine**: [`src/core/ingestion/ingestion.py`](ingestion/ingestion.py) — See [`guidelines.md`](ingestion/guidelines.md)
- 📌 **State Tracker**: [`src/core/state_tracker/state_tracker.py`](state_tracker/state_tracker.py) — See [`guidelines.md`](state_tracker/guidelines.md)
- ✂️ **Text Splitter**: [`src/core/text_splitter/text_splitter.py`](text_splitter/text_splitter.py) — See [`guidelines.md`](text_splitter/guidelines.md)

For overall module architecture, see [`guidelines.md`](guidelines.md).
