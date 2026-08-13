# 📄 Guideline: `src/vector_store/store.py` — ChromaDB Vector Store Manager

> **File**: [`store.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/vector_store/store.py)
> **Lines**: 173 | **Role**: Manages ChromaDB persistence, embedding, and hybrid retrieval
> **Module**: `src.vector_store`

---

## 1. High-Level Overview

### Purpose
`VectorStoreManager` is the **data access layer** for the vector store. It encapsulates all ChromaDB operations:
- Adding document chunks with embeddings
- Deleting vectors by source file
- Similarity search with relevance scores
- Hybrid retrieval (vector + BM25 ensemble)
- Collection statistics and reset

### Architectural Role
This module sits at the bottom of the data layer stack. It is consumed by:
- `IngestionEngine` — for adding and deleting document vectors
- `RAGEngine` / `graph.py` — for searching during query time
- `app.py` — for stats display and collection reset

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Repository Pattern** | Abstracts ChromaDB operations behind a clean Python interface |
| **Facade** | Hides LangChain Chroma, embedding function, and retriever complexity |
| **Strategy** | `get_retriever()` supports two strategies: vector-only and hybrid (ensemble) |
| **Graceful Degradation** | Falls back from scored search to basic search, and from hybrid to vector-only |

---

## 2. Dependencies & Imports

### External Libraries
| Import | Purpose |
|--------|---------|
| `langchain_chroma.Chroma` | LangChain's ChromaDB wrapper |
| `langchain_classic.retrievers.EnsembleRetriever` | Combines multiple retrievers with weighted scoring |
| `langchain_community.retrievers.bm25.BM25Retriever` | BM25 keyword-based retrieval |
| `langchain_core.documents.Document` | LangChain document data structure |
| `langchain_google_genai.GoogleGenerativeAIEmbeddings` | Gemini embedding model |

### Internal Modules
| Import | Purpose |
|--------|---------|
| `src.config.settings` | API keys, model names, paths, collection config |
| `src.utils.logger` | Logging |

---

## 3. Low-Level Breakdown

### 3.1 `VectorStoreManager.__init__()` (Lines 19–38)

```python
def __init__(self, embedding_fn: Optional[Embeddings] = None):
    self.persist_dir = str(settings.VECTOR_STORE_DIR.resolve())
    self.embedding_fn = embedding_fn or get_embedding_function()
```

#### Embedding Function Setup
- Accepts an optional `Embeddings` instance via constructor injection.
- If `embedding_fn` is `None`, calls `get_embedding_function()` which retrieves the Singleton instance managed by `EmbeddingProvider`.
- Decouples `VectorStoreManager` from any single vendor (supports Google Gemini, OpenAI, etc.).

#### ChromaDB Initialization (Lines 30–35)
```python
self.vectorstore = Chroma(
    collection_name=settings.CHROMA_COLLECTION_NAME,  # "business_analyst_documents"
    embedding_function=self.embedding_fn,
    persist_directory=self.persist_dir,
    collection_metadata={"hnsw:space": "cosine"},
)
```
- `hnsw:space: "cosine"` — Uses cosine similarity (not L2 distance) for HNSW index
- Data persists to `data/vector_store/` directory

### 3.2 `add_documents()` (Lines 40–51)
```python
def add_documents(self, documents: List[Document]) -> int:
```
- Extracts `chunk_id` from each document's metadata for use as ChromaDB IDs
- Falls back to `None` (auto-generated IDs) if any chunk_id is missing
- Calls `vectorstore.add_documents()` which **embeds and upserts** all documents

### 3.3 `add_chunks()` (Lines 53–55)
```python
def add_chunks(self, chunks: List[Document]) -> int:
    return self.add_documents(chunks)
```
Backwards-compatible alias — used by `IngestionEngine`.

### 3.4 `delete_by_file_path()` (Lines 57–69)
```python
def delete_by_file_path(self, file_path_str: str) -> int:
```
1. Accesses the **raw ChromaDB collection** via `self.vectorstore._collection`
2. Queries with `where={"source_file": file_path_str}` filter
3. Deletes all matching IDs
4. Returns count of deleted vectors

**Note**: Uses private `_collection` attribute — this is fragile and may break with LangChain updates.

### 3.5 `search()` (Lines 71–111)
```python
def search(self, query, top_k, similarity_threshold) -> List[Dict[str, Any]]:
```

**Primary path** (Lines 83–95):
```python
results_with_score = self.vectorstore.similarity_search_with_relevance_scores(
    query=query, k=top_k
)
```
- Returns `(Document, score)` tuples
- Filters by `similarity_threshold`
- Wraps each result in a dict: `{"content", "metadata", "similarity_score"}`

**Fallback path** (Lines 96–108):
- If scored search fails, falls back to basic `similarity_search()`
- Assigns a default score of `0.5` to all results

**Post-processing** (Line 110):
```python
matched_items.sort(key=lambda x: x["similarity_score"], reverse=True)
```
Sorts results by descending similarity score.

### 3.6 `get_retriever()` (Lines 113–148)
```python
def get_retriever(self, top_k, use_hybrid=True):
```

#### Vector Retriever (Lines 119–122)
```python
vector_retriever = self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": top_k},
)
```

#### Hybrid Path (Lines 127–142)
```python
bm25_retriever = BM25Retriever.from_documents(docs)
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4],
)
```
- Retrieves **all** documents from ChromaDB to build BM25 index
- 60% weight on vector similarity, 40% weight on BM25 keyword matching
- Falls back to vector-only if BM25 initialization fails

**Note**: Loading all documents for BM25 is expensive for large collections.

### 3.7 `get_stats()` (Lines 150–157)
```python
def get_stats(self) -> Dict[str, Any]:
    total_chunks = self.vectorstore._collection.count()
    return {
        "total_chunks": total_chunks,
        "collection_name": settings.CHROMA_COLLECTION_NAME,
        "vector_store_path": self.persist_dir,
    }
```
- Uses private `_collection.count()` for chunk count

### 3.8 `clear_all()` (Lines 159–171)
```python
def clear_all(self) -> None:
    self.vectorstore.delete_collection()
    self.vectorstore = Chroma(...)  # Re-create
```
- Deletes the entire ChromaDB collection
- Re-initializes a fresh collection with the same configuration
- Called by the UI's "Clear All" button

---

## 4. Data Flow

### Write Path (Ingestion)
```
List[Document] (with chunk_ids)
       │
       ▼
add_documents() → embedding_fn(texts) → ChromaDB upsert
```

### Read Path (Query)
```
query string
       │
       ▼
search() → embedding_fn(query) → ChromaDB cosine similarity
       │
       ▼
[{content, metadata, similarity_score}, ...]
```

### Delete Path (Eviction)
```
source_file path string
       │
       ▼
delete_by_file_path() → ChromaDB.get(where=...) → ChromaDB.delete(ids=...)
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Private API Usage** | `_collection` is a private attribute of LangChain Chroma | Use public API methods or ChromaDB client directly |
| **BM25 Scalability** | `get_retriever()` loads ALL documents for BM25 index | Build BM25 index incrementally, or use a persistent BM25 store |
| **Embedding Batching** | `add_documents()` embeds all chunks in one API call | Add batch size control for large ingestion runs |
| **Connection Pooling** | New Chroma instance created on clear; no connection management | Use a connection pool or client factory |
| **Metadata Search** | No method for metadata-based filtering (e.g., find all chunks from a specific file) | Add `search_by_metadata()` method |
| **Caching** | Every `search()` call embeds the query | Add query embedding cache (LRU) for repeated queries |
| **Hybrid Retriever** | `get_retriever()` is defined but not used anywhere in the codebase | Either integrate it into the RAG pipeline or remove dead code |
