import time

import streamlit as st

from src.config import settings
from src.core.ingestion import IngestionEngine
from src.core.state_tracker import StateTracker
from src.llm.rag_engine import RAGEngine
from src.vector_store.store import VectorStoreManager

# Configure Streamlit page layout and title
st.set_page_config(
    page_title="Business Analyst RAG - Gemini",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics and clean typography
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .hero-card {
        background-color: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .citation-box {
        background-color: #F1F5F9;
        border-left: 4px solid #3B82F6;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.88rem;
        border-radius: 4px;
    }
    .badge-indexed {
        background-color: #DCFCE7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize persistent components in Streamlit Session State
if "state_tracker" not in st.session_state:
    st.session_state.state_tracker = StateTracker()

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStoreManager()

if "ingestion_engine" not in st.session_state:
    st.session_state.ingestion_engine = IngestionEngine(
        state_tracker=st.session_state.state_tracker,
        vector_store=st.session_state.vector_store,
    )

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine(
        vector_store=st.session_state.vector_store,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

stats = st.session_state.vector_store.get_stats()
all_states = st.session_state.state_tracker.get_all_states()
has_documents = len(all_states) > 0 and stats.get("total_chunks", 0) > 0

# --- SIDEBAR ---
with st.sidebar:
    st.title("📊 Business Analyst RAG")
    st.caption("Powered by Google Gemini & ChromaDB")

    st.markdown("---")
    st.subheader("📁 Document Management")

    # File Upload Widget
    uploaded_files = st.file_uploader(
        "Upload Business Documents",
        type=["pdf", "docx", "xlsx", "xls", "csv", "txt", "md"],
        accept_multiple_files=True,
        key="sidebar_uploader",
        help="Upload PDF, DOCX, Excel/CSV, or Text files to data/documents/",
    )

    if uploaded_files:
        files_saved = 0
        for uploaded_file in uploaded_files:
            target_path = settings.DOCUMENTS_DIR / uploaded_file.name
            with open(target_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            files_saved += 1
        st.success(f"Saved {files_saved} file(s) to document folder!")

    # Ingestion Button
    if st.button("🔄 Sync & Ingest Documents", width="stretch", type="primary", key="sidebar_sync"):
        with st.spinner("Processing document changes and updating vector index..."):
            progress_bar = st.progress(0)
            for i in range(50):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            result = st.session_state.ingestion_engine.run()

            for i in range(50, 100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            progress_bar.empty()

        if result.errors:
            st.error(f"Ingestion completed with {len(result.errors)} error(s).")
            for err in result.errors:
                st.caption(f"⚠️ {err}")
        else:
            st.success(
                f"Sync complete! Chunks added/updated: {result.processed_chunks}, Files evicted: {result.deleted_count}"
            )
            st.rerun()

    st.markdown("---")
    st.subheader("📚 Document Library State")

    # Document Status Table
    if all_states:
        table_data = []
        for path_str, state in all_states.items():
            size_kb = round(state.file_size_bytes / 1024, 1)
            table_data.append(
                {
                    "File Name": state.file_name,
                    "Size": f"{size_kb} KB",
                    "Chunks": state.chunk_count,
                    "Status": state.status,
                }
            )
        st.dataframe(table_data, width="stretch", hide_index=True)
    else:
        st.info("No documents indexed yet. Drop files in `data/documents/` and click Sync!")

    st.markdown("---")
    st.subheader("⚙️ RAG Configuration")

    model_option = st.selectbox(
        "Gemini LLM Model",
        options=["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
    )

    st.session_state.rag_engine.set_model(model_option)

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
    top_k = st.slider(
        "Top-K Retrieved Chunks", min_value=1, max_value=15, value=settings.TOP_K_RETRIEVAL
    )
    similarity_thresh = st.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=0.9,
        value=settings.SIMILARITY_THRESHOLD,
        step=0.05,
    )

    st.markdown(f"**Total Chunks in Vector DB**: `{stats['total_chunks']}`")

    st.markdown("---")
    st.markdown("📖 [Master Guidelines](guidelines.md)")

# --- MAIN PANEL ---
st.markdown('<div class="main-title">Business Analyst RAG Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Synthesize financial data, extract market insights, and analyze strategic business documents powered by Google Gemini</div>',
    unsafe_allow_html=True,
)

if not has_documents:
    with st.container():
        st.info(
            "💡 **Getting Started**: Upload your business documents to enable context-grounded analysis!"
        )
        with st.expander("📁 **Upload Documents to Chat Center**", expanded=True):
            st.markdown(
                "Upload your financial reports, quarterly filings, strategic plans, or datasets (PDF, DOCX, CSV, Excel, TXT, MD) below to index them into ChromaDB."
            )
            center_uploaded = st.file_uploader(
                "Select business documents",
                type=["pdf", "docx", "xlsx", "xls", "csv", "txt", "md"],
                accept_multiple_files=True,
                key="center_uploader",
            )
            if center_uploaded:
                saved = 0
                for f in center_uploaded:
                    t_path = settings.DOCUMENTS_DIR / f.name
                    with open(t_path, "wb") as out_f:
                        out_f.write(f.getbuffer())
                    saved += 1
                st.success(f"Saved {saved} file(s) to document folder!")

            if st.button(
                "🔄 Sync & Ingest Documents Now",
                type="primary",
                key="center_sync_btn",
                width="stretch",
            ):
                with st.spinner("Indexing uploaded documents..."):
                    res = st.session_state.ingestion_engine.run()
                if res.errors:
                    st.error(f"Ingestion finished with {len(res.errors)} error(s).")
                else:
                    st.success(f"Successfully indexed {res.processed_chunks} chunk(s)!")
                    st.rerun()

# Suggested Business Prompts
st.caption("💡 **Quick Starter Questions**:")
col1, col2, col3, col4 = st.columns(4)

selected_prompt = None
with col1:
    if st.button("📊 Revenue & Growth Trends", width="stretch"):
        selected_prompt = "Synthesize key revenue growth drivers and quarterly financial performance across the uploaded business documents."
with col2:
    if st.button("⚠️ Key Operational Risks", width="stretch"):
        selected_prompt = "Identify the major operational, financial, and strategic risks highlighted in the documents."
with col3:
    if st.button("📈 Table & Data Metrics", width="stretch"):
        selected_prompt = (
            "Extract and summarize all major quantitative metrics, tables, and financial totals."
        )
with col4:
    if st.button("📋 Executive Action Items", width="stretch"):
        selected_prompt = "Summarize the critical action items, recommendations, and strategic priorities for management."

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("thoughts") or msg.get("decision_log"):
            with st.expander("🧠 View Agent Thinking & Decision Process", expanded=False):
                if msg.get("decision_log"):
                    st.markdown("\n\n".join(msg["decision_log"]))
                if msg.get("thoughts"):
                    st.markdown("--- \n**💭 Thought Process:**")
                    st.markdown(f"```text\n{msg['thoughts']}\n```")

        if "citations" in msg and msg["citations"]:
            with st.expander("📚 Source Citations & References", expanded=False):
                for idx, cit in enumerate(msg["citations"]):
                    st.markdown(
                        f"**{idx+1}. {cit.file_name}** (`{cit.page_or_section}`) - Match: `{cit.similarity_score}`\n"
                        f'> *"{cit.snippet}"*'
                    )

# Process User Input
prompt_input = st.chat_input("Ask a question about business concepts or uploaded documents...")
final_query = selected_prompt or prompt_input

if final_query:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(final_query)

    # Generate assistant response
    with st.chat_message("assistant"):
        status_container = st.status("🧠 Agent Thinking & Decision Process", expanded=True)
        status_log_placeholder = status_container.empty()
        thought_header_placeholder = status_container.empty()
        thought_content_placeholder = status_container.empty()
        message_placeholder = st.empty()

        status_logs = []
        accumulated_thoughts = ""
        full_response = ""

        # Build history string
        history_str = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-6:]]
        )

        try:
            stream_iter, citations = st.session_state.rag_engine.query_stream(
                user_query=final_query,
                chat_history_str=history_str,
                top_k=top_k,
                similarity_threshold=similarity_thresh,
                temperature=temperature,
            )

            for event_type, payload in stream_iter:
                if event_type == "status":
                    status_logs.append(payload)
                    status_log_placeholder.markdown("\n\n".join(status_logs))
                elif event_type == "thought":
                    if not accumulated_thoughts:
                        thought_header_placeholder.markdown(
                            "--- \n**💭 Model Reasoning Thought Process:**"
                        )
                    accumulated_thoughts += payload
                    thought_content_placeholder.markdown(f"```text\n{accumulated_thoughts}\n```")
                elif event_type == "answer":
                    full_response += payload
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            status_container.update(
                label="🧠 Agent Decision Process Complete", state="complete", expanded=False
            )

            if citations:
                with st.expander("📚 Source Citations & References", expanded=False):
                    for idx, cit in enumerate(citations):
                        st.markdown(
                            f"**{idx+1}. {cit.file_name}** (`{cit.page_or_section}`) - Match: `{cit.similarity_score}`\n"
                            f'> *"{cit.snippet}"*'
                        )

            # Store in session state
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "citations": citations,
                    "thoughts": accumulated_thoughts,
                    "decision_log": status_logs,
                }
            )

        except Exception as e:
            status_container.update(
                label="⚠️ Error in Agent Processing", state="error", expanded=True
            )
            st.error(f"Error generating response: {str(e)}")
