import os
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings
from src.llm.graph import build_rag_graph
from src.llm.prompts import BUSINESS_ANALYST_SYSTEM_PROMPT
from src.utils.logger import get_logger
from src.vector_store.store import VectorStoreManager

logger = get_logger("rag_engine")


def extract_text_content(content: Any) -> str:
    """Extracts plain text string from LLM chunk content (handles string, list, or dict)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        res = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                res.append(str(item["text"]))
            elif isinstance(item, str):
                res.append(item)
        return "".join(res)
    return str(content) if content is not None else ""


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
    """Conversational RAG Pipeline powered by LangChain & LangGraph."""

    def __init__(
        self,
        vector_store: Optional[VectorStoreManager] = None,
        model_name: Optional[str] = None,
    ):
        self.vector_store = vector_store or VectorStoreManager()
        self.model_name = model_name or settings.GEMINI_LLM_MODEL
        self._graph = None

    @property
    def graph(self):
        if self._graph is None:
            self._graph = build_rag_graph(self.vector_store, self.model_name)
        return self._graph

    def set_model(self, model_name: str):
        """Updates model name dynamically."""
        if self.model_name != model_name:
            self.model_name = model_name
            self._graph = build_rag_graph(self.vector_store, self.model_name)

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
        """Executes full RAG query cycle using LangGraph."""
        input_state = {
            "question": user_query,
            "chat_history": chat_history_str,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "temperature": temperature,
        }

        output_state = self.graph.invoke(input_state)
        raw_ans = output_state.get("generation", "")
        answer = extract_text_content(raw_ans)
        raw_citations = output_state.get("citations", [])

        citations = [
            Citation(
                file_name=c.get("file_name", "Unknown File"),
                source_file=c.get("source_file", ""),
                page_or_section=c.get("page_or_section", "N/A"),
                similarity_score=c.get("similarity_score", 0.0),
                snippet=c.get("snippet", ""),
            )
            for c in raw_citations
        ]

        return RAGResponse(answer=answer, citations=citations)

    def query_stream(
        self,
        user_query: str,
        chat_history_str: str = "",
        top_k: int = settings.TOP_K_RETRIEVAL,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD,
        temperature: float = 0.2,
    ) -> Tuple[Iterator[str], List[Citation]]:
        """Executes RAG query and streams response tokens using ChatGoogleGenerativeAI."""
        matched_chunks = self.vector_store.search(
            query=user_query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        citations = self._extract_citations(matched_chunks)

        if not matched_chunks:

            def empty_gen():
                yield "No relevant business documents found in the vector store matching your query. Please upload files and click 'Sync & Ingest'."

            return empty_gen(), []

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

        context_str = "\n".join(blocks)

        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key or "placeholder_key",
            temperature=temperature,
            streaming=True,
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", BUSINESS_ANALYST_SYSTEM_PROMPT),
                (
                    "human",
                    "Conversational Context:\n{chat_history}\n\nRetrieved Business Documents Context:\n{context}\n\nBusiness Analyst Query:\n{question}",
                ),
            ]
        )

        chain = prompt_template | llm

        def stream_generator():
            for chunk in chain.stream(
                {
                    "chat_history": chat_history_str,
                    "context": context_str,
                    "question": user_query,
                }
            ):
                text_piece = extract_text_content(chunk.content)
                if text_piece:
                    yield text_piece

        return stream_generator(), citations
