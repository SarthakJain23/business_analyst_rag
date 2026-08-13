# 📄 Guideline: `src/config.py` — Centralized Application Settings

> **File**: [`config.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/config.py)
> **Lines**: 43 | **Role**: Configuration management
> **Module**: `src.config`

---

## 1. High-Level Overview

### Purpose
`config.py` is the **single source of truth** for all application configuration. It centralizes:
- API keys (loaded from `.env`)
- Model names and embedding dimensions
- File system paths (documents, vector store, metadata)
- Chunking parameters (size, overlap)
- Retrieval parameters (top-k, similarity threshold)

### Architectural Role
Every module in the project imports `settings` from this file. It acts as a **Configuration Singleton** — instantiated once at module load time, ensuring all components share the same settings.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Singleton** | `settings = Settings()` is a module-level instance, imported everywhere |
| **Configuration Object** | All settings are class attributes on a single `Settings` class |
| **Environment Variable Bridge** | Uses `python-dotenv` to load `.env` into `os.environ`, then reads via `os.getenv` |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `os` | Read environment variables (`os.getenv`) |
| `pathlib.Path` | Cross-platform filesystem paths |
| `dotenv.load_dotenv` | Loads `.env` file into environment |

---

## 3. Low-Level Breakdown

### 3.1 Base Directory Resolution (Line 6)
```python
BASE_DIR = Path(__file__).resolve().parent.parent
```
- `__file__` → `/path/to/src/config.py`
- `.parent` → `/path/to/src/`
- `.parent.parent` → `/path/to/business_analyst_rag/` (project root)
- `.resolve()` ensures absolute path (no symlinks)

### 3.2 Environment Loading (Line 9)
```python
load_dotenv(BASE_DIR / ".env")
```
- Reads `business_analyst_rag/.env` and injects key-value pairs into `os.environ`
- Called at **module import time**, before `Settings` is instantiated

### 3.3 Settings Class (Lines 12–38)

#### API Configuration
| Attribute | Type | Default | Source |
|-----------|------|---------|--------|
| `GOOGLE_API_KEY` | `str` | `""` | `os.getenv("GOOGLE_API_KEY")` |
| `OPENAI_API_KEY` | `str` | `""` | `os.getenv("OPENAI_API_KEY")` |

#### Model Configuration
| Attribute | Type | Value | Notes |
|-----------|------|-------|-------|
| `GEMINI_LLM_MODEL` | `str` | `"gemini-3.6-flash"` | Default LLM for RAG queries |
| `EMBEDDING_VENDOR` | `str` | `"google"` | Active embedding vendor (`google` or `openai`) |
| `EMBEDDING_MODEL` | `str` | `"gemini-embedding-001"` | Active embedding model name |
| `EMBEDDING_DIMENSION` | `int` | `1536` | Output dimensionality of embeddings |

#### Path Configuration
| Attribute | Type | Value |
|-----------|------|-------|
| `DOCUMENTS_DIR` | `Path` | `BASE_DIR / "data/documents"` |
| `VECTOR_STORE_DIR` | `Path` | `BASE_DIR / "data/vector_store"` |
| `METADATA_DIR` | `Path` | `BASE_DIR / "data/metadata"` |

#### Vector Store Configuration
| Attribute | Type | Value |
|-----------|------|-------|
| `CHROMA_COLLECTION_NAME` | `str` | `"business_analyst_documents"` |

#### Chunking Configuration
| Attribute | Type | Value | Purpose |
|-----------|------|-------|---------|
| `CHUNK_SIZE` | `int` | `1000` | Max characters per text chunk |
| `CHUNK_OVERLAP` | `int` | `150` | Overlap between adjacent chunks (context preservation) |

#### Retrieval Configuration
| Attribute | Type | Value | Purpose |
|-----------|------|-------|---------|
| `TOP_K_RETRIEVAL` | `int` | `5` | Number of top chunks to retrieve |
| `SIMILARITY_THRESHOLD` | `float` | `0.3` | Minimum cosine similarity for inclusion |

### 3.4 `ensure_directories()` Method (Lines 34–38)
```python
def ensure_directories(self):
    self.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    self.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    self.METADATA_DIR.mkdir(parents=True, exist_ok=True)
```
- Creates all three data directories if they don't exist
- `parents=True` creates intermediate directories
- `exist_ok=True` prevents errors if already present

### 3.5 Module-Level Instantiation (Lines 41–42)
```python
settings = Settings()
settings.ensure_directories()
```
- Creates the singleton **at import time**
- Immediately ensures directories exist
- Any module doing `from src.config import settings` gets this pre-initialized instance

---

## 4. Data Flow

```
.env file → load_dotenv() → os.environ
                                  │
                                  ▼
                        Settings class attributes
                                  │
                                  ▼
              settings singleton (used by all modules)
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Type Safety** | `Settings` is a plain class with class-level attributes, not validated | Use `pydantic-settings.BaseSettings` (already a dependency) for runtime validation and `.env` auto-loading |
| **Immutability** | Settings can be mutated at runtime (e.g., `settings.CHUNK_SIZE = 500`) | Use `@dataclass(frozen=True)` or Pydantic's `model_config = ConfigDict(frozen=True)` |
| **Environment Separation** | No concept of dev/staging/production profiles | Add an `ENV` variable to select config profiles |
| **Secrets Management** | API key defaults to empty string silently | Raise a startup warning/error if `GOOGLE_API_KEY` is empty |
| **Path Hardcoding** | Data paths are hardcoded relative to `BASE_DIR` | Allow override via environment variables (e.g., `DOCUMENTS_DIR` env var) |
