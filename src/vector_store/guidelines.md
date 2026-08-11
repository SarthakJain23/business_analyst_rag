# Vector Store Module - Guidelines

## Purpose
The `src/vector_store/` module abstracts local vector database operations using **ChromaDB** and generates embeddings using Google's **`gemini-embedding-001`** model.

## Structural Design & Guidelines

1. **Local Persistence (`store.py`)**:
   - Uses `chromadb.PersistentClient` pointing to `data/vector_store/`.
   - Maintains a dedicated collection named `business_analyst_documents`.

2. **Embedding Function**:
   - Wraps Google Generative AI Embedding API to convert text chunks into vector embeddings using `models/gemini-embedding-001` (or `gemini-embedding-001`).
   - Implements robust error handling and batching for embedding requests.

3. **Operations Contract**:
   - `add_documents(chunks: List[DocumentChunk])`: Inserts or updates chunk vectors with full metadata.
   - `delete_by_file_path(file_path: str)`: Deletes all vectors corresponding to a specific document.
   - `search(query: str, top_k: int, similarity_threshold: float)`: Performs cosine similarity search and returns matched document chunks along with similarity scores.
   - `get_stats()`: Returns total document count, total chunk count, and database size.

---
