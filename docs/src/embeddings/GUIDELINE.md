# 📄 Guideline: `src/embeddings/provider.py` — Vendor-Agnostic Embedding Provider

> **File**: [`provider.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/embeddings/provider.py)
> **Lines**: ~170 | **Role**: Module-Level Singleton & Factory for Embedding Models
> **Module**: `src.embeddings`

---

## 1. High-Level Overview

### Purpose

`provider.py` provides a **vendor-agnostic embedding management system**. It decouples the vector store and application logic from any specific embedding provider (e.g. Google Gemini or OpenAI).

It implements a **Module-Level Singleton Pattern** via `_embedding_instance` to ensure that **only one single embedding model instance** exists in memory at any given time, re-instantiating only when the selected vendor or model changes.

### Supported Vendors & Models

- **Google Gemini** (`EmbeddingVendor.GOOGLE`): `gemini-embedding-001`, `gemini-embedding-2`
- **OpenAI** (`EmbeddingVendor.OPENAI`): `text-embedding-3-small`, `text-embedding-3-large`

### Architectural Role

- **Factory & Registry**: Maintains `VENDOR_MODELS` registry mapping vendors to their available models, default dimensions, and descriptions.
- **Lazy Imports**: Imports vendor-specific packages (`langchain_google_genai`, `langchain_openai`) only when that specific vendor is instantiated.
- **Singleton Lifecycle**: `get_embedding_function()` returns the cached embedding instance. Calling `reset_embedding_instance()` invalidates the cached instance (e.g. when switching vendors from UI).

### Design Patterns Used

| Pattern                    | Usage                                                                           |
| -------------------------- | ------------------------------------------------------------------------------- |
| **Module-Level Singleton** | `_embedding_instance` module state guarantees single instance in memory         |
| **Factory Pattern**        | `get_embedding_function()` instantiates vendor-specific `Embeddings`            |
| **Registry Pattern**       | `VENDOR_MODELS` metadata dictionary maps vendors to available models            |
| **Lazy Loading**           | Vendor packages imported inside activation branch to minimize initial load time |

---

## 2. Dependencies & Imports

| Import                                 | Purpose                                          |
| -------------------------------------- | ------------------------------------------------ |
| `enum.Enum`                            | Defines `EmbeddingVendor` string enum            |
| `langchain_core.embeddings.Embeddings` | Base interface for LangChain embedding objects   |
| `src.config.settings`                  | Reads default `EMBEDDING_VENDOR`, API keys, etc. |
| `src.utils.logger`                     | Structured logger for embedding events           |
| `langchain_google_genai` (lazy)        | Instantiated for Google Gemini embeddings        |
| `langchain_openai` (lazy)              | Instantiated for OpenAI embeddings               |

---

## 3. Low-Level Breakdown

### 3.1 `EmbeddingVendor` Enum

```python
class EmbeddingVendor(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"
```

### 3.2 `VENDOR_MODELS` Registry

Maps each vendor enum to a list of dicts containing:

- `name`: Model identifier (e.g. `"gemini-embedding-001"`, `"text-embedding-3-small"`)
- `dimension`: Vector output dimension (e.g. `1536`, `3072`)
- `description`: Summary of model characteristics

### 3.3 Singleton State

```python
_embedding_instance: Optional[Embeddings] = None
_current_vendor: Optional[EmbeddingVendor] = None
_current_model: Optional[str] = None
```

### 3.4 Public API Functions

- `get_embedding_function(...)`: Resolves vendor, model, and dimension. Returns cached instance if matching, or instantiates and caches a new one.
- `reset_embedding_instance()`: Clears `_embedding_instance`, `_current_vendor`, and `_current_model`.
- `get_current_vendor()`: Returns currently active vendor string.
- `get_current_model()`: Returns currently active model name.
- `get_model_names(vendor)`: Returns available model names for sidebar dropdowns.
- `get_model_dimension(vendor, model_name)`: Looks up output dimension.

---

## 4. Data Flow

```
User Selection (Sidebar UI or Settings)
                 │
                 ▼
get_embedding_function(vendor, model)
                 │
  ┌──────────────┴──────────────┐
  │ Cached & matches?           │
  ├─ Yes ──► Return existing    │
  └─ No  ──► Lazy-import package│
             Instantiate model  │
             Cache & return     │
                                ▼
                   LangChain Embeddings Object
                                │
                                ▼
                       VectorStoreManager
```

---

## 5. Improvement Suggestions

| Area                        | Issue                               | Suggestion                                                                  |
| --------------------------- | ----------------------------------- | --------------------------------------------------------------------------- |
| **Dynamic Model Discovery** | Model list is hardcoded in registry | Add optional API call to fetch live models from provider APIs               |
| **Additional Vendors**      | Only Google and OpenAI supported    | Easily extensible by adding enum value + branch in `get_embedding_function` |
