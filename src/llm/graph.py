import os
import warnings
from typing import Any, Dict, List, Optional, TypedDict

warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from src.config import settings
from src.llm.prompts import BUSINESS_ANALYST_SYSTEM_PROMPT
from src.utils.logger import get_logger
from src.vector_store.store import VectorStoreManager

logger = get_logger("rag_graph")


def extract_text_content(content: Any) -> str:
    """Extracts plain text string from LLM response content."""
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


def strip_thinking_tags(text: str) -> str:
    """Removes <thinking>...</thinking> block from text if present."""
    if "<thinking>" in text and "</thinking>" in text:
        after_tag = text.split("</thinking>")[-1].strip()
        return after_tag
    return text.strip()


class RAGState(TypedDict):
    question: str
    chat_history: str
    top_k: int
    similarity_threshold: float
    temperature: float
    messages: List[BaseMessage]
    citations: List[Dict[str, Any]]
    generation: str


def create_document_search_tool(
    vector_store: VectorStoreManager,
    top_k: int = 5,
    similarity_threshold: float = 0.3,
    citations_list: Optional[List[Dict[str, Any]]] = None,
):
    """Creates search_business_documents tool bound to the vector store."""

    @tool
    def search_business_documents(query: str) -> str:
        """Searches indexed business documents, financial filings, quarterly reports, and company files for specific facts, figures, revenue numbers, and corporate data."""
        stats = vector_store.get_stats()
        if stats.get("total_chunks", 0) == 0:
            return "No business documents are currently uploaded or indexed in the vector store. Please instruct the user to upload their document files (PDF, DOCX, CSV, Excel, TXT, MD) and click 'Sync & Ingest Documents'."

        matched_chunks = vector_store.search(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        if not matched_chunks:
            return "No relevant business document chunks found in the vector store matching your search query."

        if citations_list is not None:
            for match in matched_chunks:
                meta = match.get("metadata", {})
                citations_list.append(
                    {
                        "file_name": meta.get("file_name", "Unknown File"),
                        "source_file": meta.get("source_file", ""),
                        "page_or_section": meta.get("page_or_section", "N/A"),
                        "similarity_score": match.get("similarity_score", 0.0),
                        "snippet": match.get("content", "")[:300] + "...",
                    }
                )

        blocks = []
        for idx, match in enumerate(matched_chunks):
            meta = match.get("metadata", {})
            file_name = meta.get("file_name", "Unknown File")
            page_sec = meta.get("page_or_section", "N/A")
            score = match.get("similarity_score", 0.0)
            text = match.get("content", "")
            blocks.append(
                f"[Source #{idx + 1}: {file_name} | Location: {page_sec} | Match Score: {score:.2f}]\n{text}\n"
            )

        return "\n".join(blocks)

    return search_business_documents


def build_rag_graph(vector_store: VectorStoreManager, model_name: Optional[str] = None):
    """Builds and compiles a stateful Tool-Calling RAG workflow using LangGraph."""
    llm_model = model_name or settings.GEMINI_LLM_MODEL

    def agent_node(state: RAGState) -> Dict[str, Any]:
        question = state["question"]
        chat_history = state.get("chat_history", "")
        temp = state.get("temperature", 0.2)
        top_k = state.get("top_k", settings.TOP_K_RETRIEVAL)
        thresh = state.get("similarity_threshold", settings.SIMILARITY_THRESHOLD)

        citations: List[Dict[str, Any]] = []
        search_tool = create_document_search_tool(
            vector_store, top_k=top_k, similarity_threshold=thresh, citations_list=citations
        )

        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        llm_kwargs: Dict[str, Any] = {
            "model": llm_model,
            "google_api_key": api_key or None,
        }
        if temp is not None and "3.6" not in llm_model:
            llm_kwargs["temperature"] = temp

        llm = ChatGoogleGenerativeAI(**llm_kwargs)
        llm_with_tools = llm.bind_tools([search_tool])

        prompt_messages = [
            SystemMessage(content=BUSINESS_ANALYST_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Conversational Context:\n{chat_history}\n\nUser Question:\n{question}"
            ),
        ]

        state_messages = state.get("messages", [])
        if not state_messages:
            state_messages = prompt_messages

        response = llm_with_tools.invoke(state_messages)
        clean_gen = strip_thinking_tags(extract_text_content(response.content))
        return {
            "messages": state_messages + [response],
            "generation": clean_gen,
            "citations": citations,
        }

    workflow = StateGraph(RAGState)
    workflow.add_node("agent", agent_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)

    app = workflow.compile()
    return app
