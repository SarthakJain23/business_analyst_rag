from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Tuple

from src.config import settings
from src.llm.client import GeminiClient
from src.llm.prompts import BUSINESS_ANALYST_SYSTEM_PROMPT, build_rag_prompt
from src.utils.logger import get_logger
from src.vector_store.store import VectorStoreManager

logger = get_logger("rag_engine")


@dataclass
class Citation:
    file_name: str
    source_file: str
    page_or_section: str
    similarity_score: float
    snippet: str


@dataclass
class RAGResponse:
    answer: str
    citations: List[Citation]


class RAGEngine:
    """Conversational RAG Pipeline for Business Analyst Q&A."""

    def __init__(
        self,
        vector_store: VectorStoreManager = None,
        llm_client: GeminiClient = None,
    ):
        self.vector_store = vector_store or VectorStoreManager()
        self.llm_client = llm_client or GeminiClient()

    def _format_context(self, matched_chunks: List[Dict[str, Any]]) -> str:
        """Formats vector search matches into a clean prompt context block."""
        blocks = []
        for idx, match in enumerate(matched_chunks):
            meta = match.get("metadata", {})
            file_name = meta.get("file_name", "Unknown File")
            page_sec = meta.get("page_or_section", "N/A")
            score = match.get("similarity_score", 0.0)
            text = match.get("content", "")

            block = (
                f"[Source #{idx + 1}: {file_name} | Location: {page_sec} | Match Score: {score}]\n"
                f"{text}\n"
            )
            blocks.append(block)

        return "\n".join(blocks)

    def _extract_citations(self, matched_chunks: List[Dict[str, Any]]) -> List[Citation]:
        """Extracts structured citation objects from matched chunks."""
        citations = []
        for match in matched_chunks:
            meta = match.get("metadata", {})
            citations.append(
                Citation(
                    file_name=meta.get("file_name", "Unknown File"),
                    source_file=meta.get("source_file", ""),
                    page_or_section=meta.get("page_or_section", "N/A"),
                    similarity_score=match.get("similarity_score", 0.0),
                    snippet=match.get("content", "")[:300] + "...",
                )
            )
        return citations

    def query(
        self,
        user_query: str,
        chat_history_str: str = "",
        top_k: int = settings.TOP_K_RETRIEVAL,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD,
        temperature: float = 0.2,
    ) -> RAGResponse:
        """Executes full RAG query cycle synchronously."""
        matched_chunks = self.vector_store.search(
            query=user_query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        if not matched_chunks:
            return RAGResponse(
                answer="No relevant documents found in the vector store matching your query. Please upload business files and run ingestion.",
                citations=[],
            )

        context_str = self._format_context(matched_chunks)
        prompt = build_rag_prompt(user_query, context_str, chat_history_str)

        answer = self.llm_client.generate_response(
            prompt=prompt,
            system_instruction=BUSINESS_ANALYST_SYSTEM_PROMPT,
            temperature=temperature,
        )

        citations = self._extract_citations(matched_chunks)
        return RAGResponse(answer=answer, citations=citations)

    def query_stream(
        self,
        user_query: str,
        chat_history_str: str = "",
        top_k: int = settings.TOP_K_RETRIEVAL,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD,
        temperature: float = 0.2,
    ) -> Tuple[Iterator[str], List[Citation]]:
        """Executes RAG query and returns a streaming response iterator alongside citations."""
        matched_chunks = self.vector_store.search(
            query=user_query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        if not matched_chunks:

            def empty_gen():
                yield "No relevant documents found in the vector store matching your query. Please check uploaded files and perform ingestion."

            return empty_gen(), []

        context_str = self._format_context(matched_chunks)
        prompt = build_rag_prompt(user_query, context_str, chat_history_str)
        stream_iter = self.llm_client.generate_stream(
            prompt=prompt,
            system_instruction=BUSINESS_ANALYST_SYSTEM_PROMPT,
            temperature=temperature,
        )

        citations = self._extract_citations(matched_chunks)
        return stream_iter, citations
