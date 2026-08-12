# 📊 Business Analyst RAG Application

An enterprise-grade, modular **Retrieval-Augmented Generation (RAG)** application tailored for business analysts, corporate strategy teams, and financial researchers. 

The application incrementally ingests corporate documents (`.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.md`) using SHA-256 state tracking, indexes vector embeddings into a local **ChromaDB** database using **Google Gemini Embeddings**, and presents a high-performance interactive **Streamlit** dashboard powered by **Google Gemini LLM** (`gemini-3.6-flash`) with real-time streaming, similarity filtering, and source citation tracking.

---

## 🛠️ Tech Stack & Technologies

| Category | Technology | Description |
| :--- | :--- | :--- |
| **User Interface** | **Streamlit** (v1.35+) | Interactive web UI with real-time streaming chat, sidebar document controls, state tracking tables, and configuration sliders. |
| **LLM Engine** | **Google Gemini API** | `gemini-3.6-flash` (with fallback to `gemini-2.5-flash` / `gemini-1.5-pro`) via official `google-genai` SDK. |
| **Embeddings** | **Google Gemini Embeddings** | `gemini-embedding-001` (or `text-embedding-004`) for high-dimensional vector representations. |
| **Vector Database** | **ChromaDB** (v0.5+) | Embedded vector database stored locally on disk (`data/vector_store/`) with custom Gemini embedding function. |
| **Document Parsers** | **PyPDF**, **python-docx**, **Pandas**, **OpenPyXL** | Multi-format parser suite supporting PDF text extraction, Word document elements, and Excel/CSV tabular conversion to Markdown. |
| **State & Config** | **Pydantic / Pydantic-Settings** | Type-safe configuration management loading environment variables from `.env`. |
| **Package Manager** | **uv** / **pip** & **Pyproject** | Fast virtual environment management and packaging with `pyproject.toml` setuptools layout. |

---

## ✨ Key Features

- 📁 **Multi-Format Document Ingestion**: Seamlessly handles PDF reports, Word documents, Excel spreadsheets, CSV data, and Plaintext/Markdown notes. Tabular data from Excel/CSV is parsed directly into Markdown tables for optimal LLM context retention.
- ⚡ **Incremental State Sync (SHA-256)**: Tracks file contents on disk (`data/documents/`) using SHA-256 hashing. Automatically detects `ADDED`, `MODIFIED`, and `DELETED` files—re-indexing only modified content and evicting deleted documents without full database rebuilds.
- 🧠 **Tailored Business Analyst Persona**: Pre-configured system prompts designed for financial trend analysis, risk identification, quantitative metric extraction, and strict evidence-backed citations.
- 💬 **Interactive RAG Chat UI**: Streamlined chat interface featuring response streaming, customizable retrieval parameters (`Top-K`, `Similarity Threshold`, `Temperature`), and collapsible source citations with relevance match scores.
- 🔒 **Privacy & Local Persistence**: Vector embeddings and state tracking metadata are stored entirely on your local machine under `data/`.

---

## 📁 Project Architecture

```
business_analyst_rag/
├── .env                         # Environment variables (API keys, models, paths)
├── .env.example                 # Configuration template file
├── .gitignore                   # Version control exclusions
├── pyproject.toml               # Package configuration & Pyright settings
├── requirements.txt             # Python dependencies
├── app.py                       # Main Streamlit UI entrypoint
├── README.md                    # Project documentation
├── guidelines.md                # Workspace architectural guidelines
├── data/                        # Local data directory
│   ├── documents/               # Input folder for business documents
│   ├── metadata/                # State tracking JSON database (file hashes)
│   └── vector_store/            # ChromaDB local persistence folder
└── src/                         # Core Python package
    ├── config.py                # Pydantic settings schema & path definitions
    ├── core/                    # Ingestion pipeline & document chunking
    │   ├── ingestion.py         # Main orchestration pipeline (Sync & Indexing)
    │   ├── state_tracker.py     # SHA-256 file hashing & incremental status
    │   └── text_splitter.py     # Recursive character text chunking
    ├── llm/                     # Gemini API client & RAG execution
    │   ├── graph.py             # LangGraph workflow pipeline definition
    │   ├── prompts.py           # Business Analyst persona prompt templates
    │   └── rag_engine.py        # Vector retrieval + streaming prompt pipeline
    ├── loaders/                 # Format-specific document extractors
    │   ├── base.py              # Abstract BaseLoader returning LangChain Document objects
    │   ├── docx_loader.py       # Microsoft Word parser
    │   ├── excel_loader.py      # Excel (.xlsx/.xls) & CSV table parser
    │   ├── factory.py           # Auto-detection loader factory
    │   ├── pdf_loader.py        # PDF text parser
    │   └── text_loader.py       # Plaintext & Markdown parser
    ├── utils/                   # Shared logging utilities
    │   └── logger.py            # Formatted stdout logging handler
    └── vector_store/            # ChromaDB integration
        └── store.py             # Vector store manager & Gemini embedding function
```

---

## 🚀 Setup & Installation Guide

### Prerequisites
- **Python 3.10+** installed on your system.
- A **Google Gemini API Key** (obtainable from [Google AI Studio](https://aistudio.google.com/)).
- *(Recommended)* [`uv`](https://github.com/astral-sh/uv) package manager for ultra-fast dependency installation.

### Step 1: Clone & Navigate to Repository
```bash
cd business_analyst_rag
```

### Step 2: Configure Environment Variables
Copy `.env.example` to create your active `.env` file:
```bash
cp .env.example .env
```
Open `.env` and enter your **Google Gemini API Key**:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### Step 3: Setup Virtual Environment & Install Dependencies

#### Using `uv` (Recommended):
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate    # On macOS/Linux
# .venv\Scripts\activate     # On Windows

# Install dependencies and package in editable mode
uv pip install -r requirements.txt
uv pip install -e .
```

#### Using Standard `pip`:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate    # On macOS/Linux
# .venv\Scripts\activate     # On Windows

# Install dependencies and package in editable mode
pip install -r requirements.txt
pip install -e .
```

---

## 🖥️ Running the Application

1. **Add Business Documents**:
   Drop your files (`.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.md`) into the `data/documents/` directory (or use the upload feature in the UI).

2. **Launch Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```
   *(Or using `uv`: `uv run streamlit run app.py`)*

3. **Access UI**:
   Open **`http://localhost:8501`** in your web browser.

4. **Synchronize & Index**:
   Click **"🔄 Sync & Ingest Documents"** in the Streamlit sidebar to scan `data/documents/`, calculate SHA-256 hashes, generate vector embeddings, and store them in ChromaDB.

5. **Start Querying**:
   Use the quick starter prompt buttons or enter custom questions in the chat box to analyze your business documents!

---

## ⚙️ Configuration Reference

API keys are set in `.env`, while core application constants (models, paths, and retrieval defaults) are configured in `src/config.py`:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY` | *(Required)* | Google Gemini API Key. |
| `GEMINI_LLM_MODEL` | `gemini-3.6-flash` | Default Gemini model (`gemini-3.6-flash`, `gemini-2.5-flash`, `gemini-1.5-pro`). |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Model used for vector embeddings. |
| `CHUNK_SIZE` | `1000` | Target character count per chunk during document splitting. |
| `CHUNK_OVERLAP` | `150` | Overlapping character count between consecutive chunks. |
| `TOP_K_RETRIEVAL` | `5` | Number of most relevant document chunks retrieved per query. |
| `SIMILARITY_THRESHOLD` | `0.3` | Minimum cosine similarity threshold filter for vector matches. |

---

## 📜 License

This project is licensed under the MIT License.
