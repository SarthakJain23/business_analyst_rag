from typing import Any, Dict, List

import chromadb
from google import genai

from src.config import settings
from src.core.text_splitter import DocumentChunk
from src.utils.logger import get_logger

logger = get_logger("vector_store")


class GeminiEmbeddingFunction(chromadb.EmbeddingFunction):
    """Custom ChromaDB Embedding Function using Google Gemini Client API."""

    def __init__(
        self,
        api_key: str = settings.GOOGLE_API_KEY,
        model_name: str = settings.GEMINI_EMBEDDING_MODEL,
    ):
        self.api_key = api_key
        self.model_name = model_name
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def __call__(self, input: List[str]) -> List[List[float]]:
        if not self.client:
            logger.warning("No GOOGLE_API_KEY provided. Using zero embeddings fallback.")
            return [[0.0] * 768 for _ in input]

        embeddings = []
        # Batch requests to Gemini API (max 50 per call)
        batch_size = 50
        for i in range(0, len(input), batch_size):
            batch = input[i : i + batch_size]
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                )
                if hasattr(response, "embeddings") and response.embeddings:
                    for emb in response.embeddings:
                        embeddings.append(list(emb.values))
                else:
                    embeddings.extend([[0.0] * 768 for _ in batch])
            except Exception as e:
                logger.warning(
                    f"Error with embedding model {self.model_name}: {e}. Retrying with text-embedding-004..."
                )
                try:
                    response = self.client.models.embed_content(
                        model="text-embedding-004",
                        contents=batch,
                    )
                    for emb in response.embeddings:
                        embeddings.append(list(emb.values))
                except Exception as fallback_err:
                    logger.error(f"Fallback embedding failed: {fallback_err}")
                    embeddings.extend([[0.0] * 768 for _ in batch])

        return embeddings


class VectorStoreManager:
    """Manages local ChromaDB persistence and vector operations."""

    def __init__(self):
        self.persist_dir = str(settings.VECTOR_STORE_DIR.resolve())
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embedding_fn = GeminiEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"Initialized ChromaDB at {self.persist_dir} with collection '{settings.CHROMA_COLLECTION_NAME}'"
        )

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Adds document chunks into ChromaDB."""
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        # Clean metadata (ensure primitive types for ChromaDB)
        cleaned_metadatas = []
        for c in chunks:
            meta = {}
            for k, v in c.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
            cleaned_metadatas.append(meta)

        self.collection.upsert(ids=ids, documents=documents, metadatas=cleaned_metadatas)
        logger.info(f"Upserted {len(chunks)} chunks into vector store.")
        return len(chunks)

    def delete_by_file_path(self, file_path_str: str) -> int:
        """Deletes all chunks belonging to a specific file path."""
        try:
            results = self.collection.get(where={"source_file": file_path_str})
            ids_to_delete = results.get("ids", [])
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} vectors for file: {file_path_str}")
                return len(ids_to_delete)
        except Exception as e:
            logger.error(f"Error deleting vectors for {file_path_str}: {e}")
        return 0

    def search(
        self,
        query: str,
        top_k: int = settings.TOP_K_RETRIEVAL,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """Queries ChromaDB vector store and returns matched chunks with metadata and scores."""
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        matched_items = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance to similarity conversion: similarity = 1 - distance
                similarity = round(1.0 - dist, 4)
                if similarity >= similarity_threshold:
                    matched_items.append(
                        {
                            "content": doc,
                            "metadata": meta,
                            "similarity_score": similarity,
                            "distance": dist,
                        }
                    )

        # Sort by similarity score descending
        matched_items.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matched_items

    def get_stats(self) -> Dict[str, Any]:
        """Returns collection stats."""
        total_chunks = self.collection.count()
        return {
            "total_chunks": total_chunks,
            "collection_name": settings.CHROMA_COLLECTION_NAME,
            "vector_store_path": self.persist_dir,
        }
