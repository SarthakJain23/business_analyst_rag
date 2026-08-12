import os
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.prompts import ChatPromptTemplate
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


class RAGState(TypedDict):
    question: str
    chat_history: str
    top_k: int
    similarity_threshold: float
    temperature: float
    documents: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    generation: str


def build_rag_graph(vector_store: VectorStoreManager, model_name: Optional[str] = None):
    """Builds and compiles a stateful RAG workflow using LangGraph."""
    llm_model = model_name or settings.GEMINI_LLM_MODEL

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", BUSINESS_ANALYST_SYSTEM_PROMPT),
            (
                "human",
                "Conversational Context:\n{chat_history}\n\nRetrieved Business Documents Context:\n{context}\n\nBusiness Analyst Query:\n{question}",
            ),
        ]
    )

    def retrieve_node(state: RAGState) -> Dict[str, Any]:
        """Node 1: Retrieves candidate document chunks using Hybrid Vector + BM25 Retriever."""
        question = state["question"]
        top_k = state.get("top_k", settings.TOP_K_RETRIEVAL)
        thresh = state.get("similarity_threshold", settings.SIMILARITY_THRESHOLD)

        matched_chunks = vector_store.search(
            query=question,
            top_k=top_k,
            similarity_threshold=thresh,
        )

        citations = []
        for match in matched_chunks:
            meta = match.get("metadata", {})
            citations.append(
                {
                    "file_name": meta.get("file_name", "Unknown File"),
                    "source_file": meta.get("source_file", ""),
                    "page_or_section": meta.get("page_or_section", "N/A"),
                    "similarity_score": match.get("similarity_score", 0.0),
                    "snippet": match.get("content", "")[:300] + "...",
                }
            )

        return {"documents": matched_chunks, "citations": citations}

    def generate_node(state: RAGState) -> Dict[str, Any]:
        """Node 2: Generates response using Gemini LLM over retrieved contexts."""
        documents = state.get("documents", [])
        question = state["question"]
        chat_history = state.get("chat_history", "")
        temp = state.get("temperature", 0.2)

        if not documents:
            return {
                "generation": "No relevant business documents found in the vector store matching your query. Please upload documents and click 'Sync & Ingest'."
            }

        blocks = []
        for idx, match in enumerate(documents):
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

        active_llm = ChatGoogleGenerativeAI(
            model=llm_model,
            google_api_key=settings.GOOGLE_API_KEY or None,
            temperature=temp,
        )

        chain = prompt_template | active_llm
        res = chain.invoke(
            {
                "chat_history": chat_history,
                "context": context_str,
                "question": question,
            }
        )

        return {"generation": extract_text_content(res.content)}

    workflow = StateGraph(RAGState)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    app = workflow.compile()
    return app
