# Core Ingestion & State Engine - Guidelines

## Purpose
The `src/core/` module orchestrates incremental document processing, text chunking, and file state synchronization.

## Structural Design & Guidelines

1. **State Tracker (`state_tracker.py`)**:
   - Maintains `data/metadata/ingestion_state.json`.
   - Computes SHA-256 hash for every file in `data/documents/`.
   - Compares current file system state with recorded state to classify files into four categories:
     - `ADDED`: New file found on disk.
     - `MODIFIED`: File content changed (SHA-256 mismatch).
     - `DELETED`: File removed from disk since last ingestion.
     - `UNCHANGED`: File untouched (bypassed during ingestion).

2. **Text Splitter (`text_splitter.py`)**:
   - Uses recursive character text splitting with configurable chunk size (default: 1000 characters) and overlap (default: 150 characters).
   - Preserves all metadata from the parent `Document` and appends `chunk_id` and `chunk_index`.

3. **Ingestion Orchestrator (`ingestion.py`)**:
   - Atomic synchronization sequence:
     1. Query state changes via `state_tracker.get_changes()`.
     2. For `DELETED` and `MODIFIED` files, evict existing vectors from ChromaDB.
     3. For `ADDED` and `MODIFIED` files, load, chunk, and embed new vectors.
     4. Save updated state tracker state to disk.
   - Exposes clean `run_ingestion()` function returning detailed ingestion metrics (files processed, chunks created, vectors deleted, errors encountered).

---
