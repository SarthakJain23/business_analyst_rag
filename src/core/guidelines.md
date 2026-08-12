# Core Ingestion & State Engine - Guidelines

## Purpose
The `src/core/` module orchestrates incremental document processing, text chunking, and file state synchronization.

## Structural Design & Guidelines

1. **State Tracker (`src/core/state_tracker/`)**:
   - Detailed specification & code breakdown: [`guidelines.md`](state_tracker/guidelines.md)
   - Implementation: [`state_tracker.py`](state_tracker/state_tracker.py)
   - Maintains `data/metadata/ingestion_state.json`.
   - Computes SHA-256 hash for every file in `data/documents/`.
   - Compares current file system state with recorded state to classify files into four categories:
     - `INDEXED`: New or updated file successfully embedded.
     - `FAILED`: Parsing/indexing error occurred.
     - `PENDING`: Queued for processing.
     - `EMPTY`: File yielded no text content.

2. **Text Splitter (`src/core/text_splitter/`)**:
   - Detailed specification & code breakdown: [`guidelines.md`](text_splitter/guidelines.md)
   - Implementation: [`text_splitter.py`](text_splitter/text_splitter.py)
   - Uses recursive character text splitting with configurable chunk size (default: 1000 characters) and overlap (default: 150 characters).
   - Preserves all metadata from the parent `Document` and appends `chunk_id`, `chunk_index`, and `total_chunks`.

3. **Ingestion Orchestrator (`src/core/ingestion/`)**:
   - Detailed specification & code breakdown: [`guidelines.md`](ingestion/guidelines.md)
   - Implementation: [`ingestion.py`](ingestion/ingestion.py)
   - Atomic synchronization sequence:
     1. Query state changes via `state_tracker.detect_changes()`.
     2. For deleted and modified files, evict existing vectors from ChromaDB.
     3. For added and modified files, load, chunk, and embed new vectors.
     4. Save updated state tracker state to disk (`save_state()`).
   - Exposes clean `IngestionEngine.run()` method returning detailed `IngestionResult` metrics (files processed, chunks created, vectors deleted, errors encountered).
