# 📄 Guideline: `src/core/state_tracker/state_tracker.py` — Incremental Ingestion State Manager

> **File**: [`state_tracker.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/state_tracker.py)
> **Lines**: 149 | **Role**: Hash-based file change detection & persistence
> **Module**: `src.core.state_tracker`

---

## 1. High-Level Overview

### Purpose
The `StateTracker` manages **incremental ingestion** by tracking the SHA-256 hash, size, modification time, and indexing status of every processed document. On each ingestion run, it compares the current file system state against its recorded state to determine which files are **new**, **modified**, or **deleted**.

### Architectural Role
This module is a **stateful persistence layer** that enables the ingestion engine to skip unchanged files. Without it, every ingestion run would re-process all documents from scratch.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **State Pattern** | `FileState` tracks per-file state with status transitions (PENDING → INDEXED/FAILED/EMPTY) |
| **Repository Pattern** | `StateTracker` acts as a repository for `FileState` objects, with JSON file backing |
| **Change Detection / Dirty Checking** | Compares SHA-256 hashes to detect modifications |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `hashlib` | SHA-256 file hashing |
| `json` | State serialization/deserialization |
| `dataclasses` | `FileState` data structure (`@dataclass`, `asdict`) |
| `enum.Enum` | `FileStatus` enumeration |
| `pathlib.Path` | File system operations |
| `src.config.settings` | Default paths (`METADATA_DIR`, `DOCUMENTS_DIR`) |
| `src.utils.logger` | Structured logging |

---

## 3. Low-Level Breakdown

### 3.1 `FileStatus` Enum (Lines 14–18)
```python
class FileStatus(str, Enum):
    INDEXED = "indexed"
    FAILED = "failed"
    PENDING = "pending"
    EMPTY = "empty"
```
- Inherits from `str` for JSON serialization compatibility
- States: `INDEXED` (successfully processed), `FAILED` (error during ingestion), `PENDING` (not yet processed), `EMPTY` (file had no extractable content)

### 3.2 `FileState` Dataclass (Lines 21–29)
```python
@dataclass
class FileState:
    file_path: str        # Absolute resolved path
    file_name: str        # Basename (e.g., "report.pdf")
    file_hash: str        # SHA-256 hex digest
    file_size_bytes: int  # File size on disk
    last_modified: float  # os.stat().st_mtime timestamp
    chunk_count: int = 0  # Number of chunks generated
    status: FileStatus | str = FileStatus.INDEXED
```
- `status` accepts both `FileStatus` enum and `str` (to handle the `FAILED: <error>` concatenation pattern from ingestion engine)
- Uses union type `FileStatus | str` (Python 3.10+ syntax)

### 3.3 `StateTracker.__init__()` (Lines 35–38)
```python
def __init__(self, metadata_dir: Path = settings.METADATA_DIR):
    self.state_file = metadata_dir / "ingestion_state.json"
    self._state: Dict[str, FileState] = {}
    self.load_state()
```
- State file location: `data/metadata/ingestion_state.json`
- Internal state is a dictionary mapping **absolute file path strings** to `FileState` objects
- Immediately loads persisted state on construction

### 3.4 `calculate_file_hash()` (Lines 40–46)
```python
def calculate_file_hash(self, file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()
```
- Reads file in **64KB chunks** to handle large files without loading into memory
- Uses walrus operator (`:=`) for concise chunk reading
- Returns hex-encoded SHA-256 digest (64 characters)

### 3.5 `load_state()` (Lines 48–67)
```python
def load_state(self) -> None:
```
- Reads `ingestion_state.json` if it exists
- Deserializes each entry from dict → `FileState` via `FileState(**data)`
- Attempts to convert `status` strings back to `FileStatus` enum values
- Falls back to raw string if enum conversion fails (handles `"failed: error message"` pattern)
- On any read error, resets state to empty dict (no crash)

### 3.6 `save_state()` (Lines 69–77)
```python
def save_state(self) -> None:
```
- Creates parent directories if needed
- Serializes `_state` dict using `dataclasses.asdict()` for each `FileState`
- Writes with `indent=2` for human-readable JSON

### 3.7 `detect_changes()` (Lines 79–111)
```python
def detect_changes(
    self, documents_dir: Path = settings.DOCUMENTS_DIR
) -> Tuple[List[Path], List[str], List[str]]:
```

**Algorithm**:
1. **Scan disk**: `documents_dir.rglob("*")` finds all files recursively, excluding hidden files (`.` prefix)
2. **Compare hashes**: For each file on disk, compute SHA-256 and compare with recorded hash
3. **Classify**:
   - If no recorded state OR hash differs → `added_or_modified`
   - If hash matches → `unchanged`
   - If recorded but not on disk → `deleted_paths` (via set difference)

**Returns**: `(added_or_modified: List[Path], deleted_paths: List[str], unchanged: List[str])`

**Performance Note**: This computes SHA-256 for *every* file on disk each time, which is O(total_file_size). For very large document sets, a faster pre-filter (e.g., mtime check) could be added.

### 3.8 `update_file_state()` (Lines 113–130)
```python
def update_file_state(
    self, file_path: Path, file_hash: str, chunk_count: int,
    status: FileStatus | str = FileStatus.INDEXED,
) -> None:
```
- Resolves the path to absolute string
- Reads current `stat()` for size and mtime
- Creates/updates `FileState` entry in `_state` dict

### 3.9 `remove_file_state()` (Lines 132–134)
- Deletes a path entry from `_state` dict (for evicted files)

### 3.10 `get_all_states()` (Lines 136–137)
- Returns a **shallow copy** of the state dict (prevents external mutation)

### 3.11 `clear_all()` (Lines 139–147)
- Empties `_state` dict
- Deletes `ingestion_state.json` from disk
- Used by the "Clear All" button in the UI

---

## 4. Data Flow

```
documents_dir (file system)
        │
        ▼
detect_changes() ──→ SHA-256 hash comparison
        │                     │
        ▼                     ▼
  added/modified        deleted paths
        │                     │
        ▼                     ▼
update_file_state()   remove_file_state()
        │                     │
        └─────────┬───────────┘
                  ▼
            save_state()
                  │
                  ▼
        ingestion_state.json
```

### JSON State File Format
```json
{
  "/absolute/path/to/report.pdf": {
    "file_path": "/absolute/path/to/report.pdf",
    "file_name": "report.pdf",
    "file_hash": "a1b2c3d4e5f6...",
    "file_size_bytes": 245760,
    "last_modified": 1723574400.0,
    "chunk_count": 12,
    "status": "indexed"
  }
}
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Performance** | Hashes every file on each detect_changes call | Add mtime pre-filter: only hash if `st_mtime` changed |
| **Atomicity** | `save_state()` writes directly to state file | Write to temp file first, then atomic rename |
| **Status Typing** | `status: FileStatus | str` allows arbitrary strings | Use `FileStatus` enum only + separate `error_message: Optional[str]` field |
| **Concurrency** | No locking on state file | Add file lock (`fcntl.flock` or `portalocker`) for multi-process safety |
| **Test Coverage** | No unit tests visible | Add tests for hash computation, change detection edge cases, JSON round-trip |
