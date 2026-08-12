import os
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("vector_store")


class VectorStoreManager:
    """Manages local ChromaDB persistence and hybrid retrieval using LangChain."""

    def __init__(self):
        self.persist_dir = str(settings.VECTOR_STORE_DIR.resolve())
        model_name = settings.GEMINI_EMBEDDING_MODEL
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        self.embedding_fn = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=api_key or "placeholder_api_key",
        )
        self.vectorstore = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            persist_directory=self.persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"Initialized LangChain ChromaDB at {self.persist_dir} with collection '{settings.CHROMA_COLLECTION_NAME}'"
        )

    def add_documents(self, documents: List[Document]) -> int:
        """Adds document chunks into ChromaDB."""
        if not documents:
            return 0

        ids = [doc.metadata.get("chunk_id") for doc in documents]
        if any(i is None for i in ids):
            ids = None

        self.vectorstore.add_documents(documents=documents, ids=ids)
        logger.info(f"Upserted {len(documents)} document chunks into vector store.")
        return len(documents)

    def add_chunks(self, chunks: List[Document]) -> int:
        """Backwards compatible alias for add_documents."""
        return self.add_documents(chunks)

    def delete_by_file_path(self, file_path_str: str) -> int:
        """Deletes all vectors belonging to a specific source file path."""
        try:
            col = self.vectorstore._collection
            results = col.get(where={"source_file": file_path_str})
            ids_to_delete = results.get("ids", [])
            if ids_to_delete:
                col.delete(ids=ids_to_delete)
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
        if self.vectorstore._collection.count() == 0:
            return []

        matched_items = []
        try:
            results_with_score = self.vectorstore.similarity_search_with_relevance_scores(
                query=query, k=top_k
            )
            for doc, score in results_with_score:
                sim_score = round(float(score), 4)
                if sim_score >= similarity_threshold:
                    matched_items.append(
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "similarity_score": sim_score,
                        }
                    )
        except Exception as e:
            logger.warning(
                f"Similarity search with score failed, falling back to basic search: {e}"
            )
            docs = self.vectorstore.similarity_search(query=query, k=top_k)
            for doc in docs:
                matched_items.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": 0.5,
                    }
                )

        matched_items.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matched_items

    def get_retriever(
        self,
        top_k: int = settings.TOP_K_RETRIEVAL,
        use_hybrid: bool = True,
    ):
        """Returns a LangChain Retriever (Ensemble Hybrid Search or Vector Search)."""
        vector_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )

        if not use_hybrid:
            return vector_retriever

        try:
            col_docs = self.vectorstore._collection.get()
            raw_contents = col_docs.get("documents", [])
            metadatas = col_docs.get("metadatas", [])
            if raw_contents and len(raw_contents) > 0:
                docs = [
                    Document(page_content=txt, metadata=meta or {})
                    for txt, meta in zip(raw_contents, metadatas)
                ]
                bm25_retriever = BM25Retriever.from_documents(docs)
                bm25_retriever.k = top_k
                ensemble_retriever = EnsembleRetriever(
                    retrievers=[vector_retriever, bm25_retriever],
                    weights=[0.6, 0.4],
                )
                return ensemble_retriever
        except Exception as e:
            logger.warning(
                f"Could not initialize BM25 hybrid search, falling back to vector retriever: {e}"
            )

        return vector_retriever

    def get_stats(self) -> Dict[str, Any]:
        """Returns collection stats."""
        total_chunks = self.vectorstore._collection.count()
        return {
            "total_chunks": total_chunks,
            "collection_name": settings.CHROMA_COLLECTION_NAME,
            "vector_store_path": self.persist_dir,
        }
