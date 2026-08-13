# 📄 Guideline: `src/core/ingestion/ingestion.py` — Document Ingestion Orchestrator

> **File**: [`ingestion.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/ingestion/ingestion.py)
> **Lines**: 101 | **Role**: Orchestrates the full document ingestion pipeline
> **Module**: `src.core.ingestion`

---

## 1. High-Level Overview

### Purpose
The `IngestionEngine` is the **central orchestrator** for the document ingestion pipeline. It coordinates:
1. **Change Detection** — Identifies new, modified, and deleted files via `StateTracker`
2. **Loading** — Dispatches files to the correct loader via `LoaderFactory`
3. **Chunking** — Splits documents into vector-ready chunks via `TextSplitter`
4. **Indexing** — Upserts chunks into ChromaDB via `VectorStoreManager`
5. **State Updates** — Records file hashes and statuses for future incremental runs

### Architectural Role
This file implements the **Orchestrator Pattern** — it doesn't contain business logic itself but coordinates four specialized subsystems in a defined sequence. It sits between the UI layer (`app.py`) and the data layer (loaders, vector store).

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Orchestrator / Pipeline** | `run()` executes a fixed sequence: detect → evict → load → split → index → save |
| **Dependency Injection** | All dependencies (`StateTracker`, `VectorStoreManager`, `TextSplitter`) are injected via constructor with defaults |
| **Result Object** | Returns a structured `IngestionResult` dataclass instead of raw values |

---

## 2. Dependencies & Imports

### Internal Modules
| Import | Purpose |
|--------|---------|
| `src.config.settings` | Default paths and configuration |
| `src.core.state_tracker.FileStatus` | Enum for file indexing status |
| `src.core.state_tracker.StateTracker` | Hash-based change detection |
| `src.core.text_splitter.TextSplitter` | Document chunking |
| `src.loaders.factory.LoaderFactory` | File-type-based loader dispatch |
| `src.vector_store.store.VectorStoreManager` | ChromaDB operations |
| `src.utils.logger.get_logger` | Structured logging |

### Standard Library
| Import | Purpose |
|--------|---------|
| `dataclasses.dataclass` | `IngestionResult` data structure |
| `pathlib.Path` | File system paths |
| `typing` | Type annotations |

---

## 3. Low-Level Breakdown

### 3.1 `IngestionResult` Dataclass (Lines 15–21)
```python
@dataclass
class IngestionResult:
    added_or_modified_count: int
    deleted_count: int
    processed_chunks: int
    errors: List[str]
    documents_status: Dict[str, Any]
```

| Field | Type | Purpose |
|-------|------|---------|
| `added_or_modified_count` | `int` | Number of files that were new or changed |
| `deleted_count` | `int` | Number of files that were removed from disk |
| `processed_chunks` | `int` | Total chunks successfully indexed |
| `errors` | `List[str]` | Human-readable error messages for failed files |
| `documents_status` | `Dict[str, Any]` | Full state tracker snapshot after ingestion |

### 3.2 `IngestionEngine.__init__()` (Lines 27–37)
```python
def __init__(
    self,
    documents_dir: Path = settings.DOCUMENTS_DIR,
    state_tracker: Optional[StateTracker] = None,
    vector_store: Optional["VectorStoreManager"] = None,
    text_splitter: Optional[TextSplitter] = None,
):
```
- **Dependency Injection**: All four dependencies have sensible defaults
- The string type annotation `"VectorStoreManager"` is a forward reference (avoids circular imports)
- Uses `or` operator for fallback instantiation: `state_tracker or StateTracker()`

### 3.3 `IngestionEngine.run()` — The Core Pipeline (Lines 39–100)

This is the **main method** that executes the full ingestion cycle. Here's the step-by-step flow:

#### Step 1: Change Detection (Lines 42–44)
```python
added_modified, deleted_paths, unchanged = self.state_tracker.detect_changes(
    self.documents_dir
)
```
- Scans `documents_dir` recursively
- Compares SHA-256 hashes against previously recorded state
- Returns three lists: new/modified file `Path` objects, deleted file path strings, unchanged path strings

#### Step 2: Evict Deleted Files (Lines 49–52)
```python
for path_str in deleted_paths:
    self.vector_store.delete_by_file_path(path_str)
    self.state_tracker.remove_file_state(path_str)
```
- For each file that no longer exists on disk:
  1. Deletes all its vectors from ChromaDB (by `source_file` metadata filter)
  2. Removes its entry from the state tracker

#### Step 3: Process New/Modified Files (Lines 54–85)
For each changed file:

1. **Resolve path & compute hash** (Lines 55–56)
2. **Check format support** (Lines 58–60) — Skips unsupported extensions
3. **Delete old vectors** (Line 63) — Ensures clean re-indexing for modified files
4. **Load document** (Lines 64–65):
   ```python
   loader = LoaderFactory.get_loader(file_path)
   raw_docs = loader.load(file_path, file_hash)
   ```
5. **Split into chunks** (Line 66):
   ```python
   chunks = self.text_splitter.split_documents(raw_docs)
   ```
6. **Index chunks** (Lines 68–73):
   ```python
   added_count = self.vector_store.add_chunks(chunks)
   self.state_tracker.update_file_state(file_path, file_hash, len(chunks), status=FileStatus.INDEXED)
   ```
7. **Handle empty documents** (Lines 74–77): Status set to `FileStatus.EMPTY`
8. **Handle errors** (Lines 79–85): Logs error, appends to error list, sets status to `FAILED`

#### Step 4: Persist State (Line 87)
```python
self.state_tracker.save_state()
```
Writes updated file states to `data/metadata/ingestion_state.json`.

#### Step 5: Build & Return Result (Lines 89–100)
Constructs and returns an `IngestionResult` with all counts and the full state snapshot.

---

## 4. Data Flow

```
documents_dir (disk)
       │
       ▼
StateTracker.detect_changes()
       │
       ├── deleted_paths ──→ VectorStore.delete_by_file_path()
       │                     StateTracker.remove_file_state()
       │
       └── added_modified ──→ LoaderFactory.get_loader()
                                    │
                                    ▼
                              Loader.load() → List[Document]
                                    │
                                    ▼
                              TextSplitter.split_documents()
                                    │
                                    ▼
                              VectorStore.add_chunks()
                                    │
                                    ▼
                              StateTracker.update_file_state()
                                    │
                                    ▼
                              StateTracker.save_state()
                                    │
                                    ▼
                              IngestionResult
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Progress Reporting** | No progress callbacks; UI fakes progress with sleep loops | Add a callback/event mechanism: `on_file_processed(file_name, chunks_count)` |
| **Parallelism** | Files are processed sequentially | Use `concurrent.futures.ThreadPoolExecutor` for I/O-bound loading |
| **Retry Logic** | Failed files are simply logged and skipped | Add configurable retry with exponential backoff |
| **Transaction Safety** | If process crashes mid-run, state and vectors can be inconsistent | Save state after each file, not just at end |
| **Batch Size** | All chunks for a file are upserted at once | Add batched upsert for very large documents |
| **Status Enum** | Failed status concatenates enum + error string: `f"{FileStatus.FAILED}: {str(e)}"` | Use a separate `error_message` field instead |
