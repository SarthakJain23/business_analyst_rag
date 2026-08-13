import os
import warnings
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
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


class ThinkingStreamParser:
    """Helper to parse streaming LLM text chunks into ('thought', text) and ('answer', text) events."""

    def __init__(self):
        self.buffer = ""
        self.in_thinking = False

    def _find_partial_tag(self, text: str, tag: str) -> int:
        for i in range(1, len(tag)):
            if text.endswith(tag[:i]):
                return len(text) - i
        return -1

    def feed(self, chunk: str) -> List[Tuple[str, str]]:
        events = []
        self.buffer += chunk

        while True:
            if not self.in_thinking:
                tag_start = self.buffer.find("<thinking>")
                if tag_start != -1:
                    answer_part = self.buffer[:tag_start]
                    if answer_part:
                        events.append(("answer", answer_part))
                    self.buffer = self.buffer[tag_start + len("<thinking>") :]
                    self.in_thinking = True
                else:
                    partial_idx = self._find_partial_tag(self.buffer, "<thinking>")
                    if partial_idx != -1:
                        answer_part = self.buffer[:partial_idx]
                        if answer_part:
                            events.append(("answer", answer_part))
                        self.buffer = self.buffer[partial_idx:]
                        break
                    else:
                        if self.buffer:
                            events.append(("answer", self.buffer))
                            self.buffer = ""
                        break
            else:
                tag_end = self.buffer.find("</thinking>")
                if tag_end != -1:
                    thought_part = self.buffer[:tag_end]
                    if thought_part:
                        events.append(("thought", thought_part))
                    self.buffer = self.buffer[tag_end + len("</thinking>") :]
                    self.in_thinking = False
                else:
                    partial_idx = self._find_partial_tag(self.buffer, "</thinking>")
                    if partial_idx != -1:
                        thought_part = self.buffer[:partial_idx]
                        if thought_part:
                            events.append(("thought", thought_part))
                        self.buffer = self.buffer[partial_idx:]
                        break
                    else:
                        if self.buffer:
                            events.append(("thought", self.buffer))
                            self.buffer = ""
                        break
        return events

    def flush(self) -> List[Tuple[str, str]]:
        events = []
        if self.buffer:
            event_type = "thought" if self.in_thinking else "answer"
            events.append((event_type, self.buffer))
            self.buffer = ""
        return events


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
    """Conversational Tool-Calling RAG Agent Pipeline powered by LangChain & LangGraph."""

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
        """Executes full query cycle using LangGraph Tool-Calling Agent."""
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
    ) -> Tuple[Iterator[Tuple[str, str]], List[Citation]]:
        """Executes Tool-Calling Agent query and streams response tokens + thinking process + status events."""
        stats = self.vector_store.get_stats()
        has_docs = stats.get("total_chunks", 0) > 0

        citations: List[Citation] = []

        @tool
        def search_business_documents(query: str) -> str:
            """Searches indexed business documents, financial filings, quarterly reports, and company files for specific facts, figures, revenue numbers, and corporate data."""
            if not has_docs:
                return "No business documents are currently uploaded or indexed in the vector store. Please instruct the user to upload their document files (PDF, DOCX, CSV, Excel, TXT, MD) and click 'Sync & Ingest Documents'."

            matched_chunks = self.vector_store.search(
                query=query,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
            )

            if not matched_chunks:
                return "No relevant business document chunks found matching the search query and similarity threshold."

            extracted = self._extract_citations(matched_chunks)
            citations.extend(extracted)

            blocks = []
            for idx, match in enumerate(matched_chunks):
                meta = match.get("metadata", {})
                file_name = meta.get("file_name", "Unknown File")
                page_sec = meta.get("page_or_section", "N/A")
                score = match.get("similarity_score", 0.0)
                text = match.get("content", "")

                block = (
                    f"[Source #{idx + 1}: {file_name} | Location: {page_sec} | Match Score: {score:.2f}]\n"
                    f"{text}\n"
                )
                blocks.append(block)

            return "\n".join(blocks)

        def stream_generator():
            api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
            llm_kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "google_api_key": api_key or None,
                "streaming": True,
            }
            if temperature is not None and "3.6" not in self.model_name:
                llm_kwargs["temperature"] = temperature

            llm = ChatGoogleGenerativeAI(**llm_kwargs)
            llm_with_tools = llm.bind_tools([search_business_documents])

            messages = [
                SystemMessage(content=BUSINESS_ANALYST_SYSTEM_PROMPT),
                HumanMessage(
                    content=f"Conversational Context:\n{chat_history_str}\n\nUser Question:\n{user_query}"
                ),
            ]

            yield (
                "status",
                "🤖 **Agent Thinking**: Evaluating query & determining tool invocation requirements...",
            )

            parser = ThinkingStreamParser()
            tool_calls_detected = []

            for chunk in llm_with_tools.stream(messages):
                if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                    for tc in chunk.tool_calls:
                        if tc not in tool_calls_detected:
                            tool_calls_detected.append(tc)
                elif (
                    hasattr(chunk, "additional_kwargs") and "tool_calls" in chunk.additional_kwargs
                ):
                    for tc in chunk.additional_kwargs["tool_calls"]:
                        if tc not in tool_calls_detected:
                            tool_calls_detected.append(tc)

                text_piece = extract_text_content(chunk.content)
                if text_piece:
                    for ev_type, ev_val in parser.feed(text_piece):
                        yield (ev_type, ev_val)

            for ev_type, ev_val in parser.flush():
                yield (ev_type, ev_val)

            if tool_calls_detected:
                for tc in tool_calls_detected:
                    tool_name = (
                        tc.get("name", "search_business_documents")
                        if isinstance(tc, dict)
                        else getattr(tc, "name", "search_business_documents")
                    )
                    tool_args = (
                        tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
                    )
                    search_query = (
                        tool_args.get("query", user_query)
                        if isinstance(tool_args, dict)
                        else user_query
                    )

                    yield (
                        "status",
                        f"🛠️ **Tool Invoked**: `{tool_name}(query='{search_query}')` | Searching Vector DB...",
                    )

                    tool_result = search_business_documents.invoke({"query": search_query})

                    yield (
                        "status",
                        f"📄 **Tool Response Received**: Synthesizing context-grounded response ({len(citations)} source citation(s) retrieved)...",
                    )

                    synthesis_messages = [
                        SystemMessage(content=BUSINESS_ANALYST_SYSTEM_PROMPT),
                        HumanMessage(
                            content=f"Conversational Context:\n{chat_history_str}\n\nRetrieved Document Tool Results:\n{tool_result}\n\nUser Question:\n{user_query}"
                        ),
                    ]

                    synthesis_parser = ThinkingStreamParser()
                    for s_chunk in llm.stream(synthesis_messages):
                        s_text = extract_text_content(s_chunk.content)
                        if s_text:
                            for ev_type, ev_val in synthesis_parser.feed(s_text):
                                yield (ev_type, ev_val)
                    for ev_type, ev_val in synthesis_parser.flush():
                        yield (ev_type, ev_val)
            else:
                yield (
                    "status",
                    "⚡ **Agent Decision**: Direct Senior Analyst Response (No document search required)",
                )

        return stream_generator(), citations
