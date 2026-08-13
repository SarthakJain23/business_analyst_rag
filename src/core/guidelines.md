# Core Ingestion & State Engine - Guidelines

## Folder & Module Context

The [`src/core/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core) module forms the data processing backbone of the Business Analyst RAG pipeline.

It manages incremental file change detection, document text chunking, and vector database synchronization to ensure that document modifications or deletions on disk (`data/documents/`) are seamlessly reflected in the ChromaDB vector store without costly, redundant re-embedding.

### Submodules & Responsibilities:
1. **State Tracker** ([`src/core/state_tracker/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker)): Maintains SHA-256 hash checksums in `data/metadata/ingestion_state.json` to detect added, modified, deleted, or unchanged files.
2. **Text Splitter** ([`src/core/text_splitter/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/text_splitter)): Splits parsed document objects into context-preserving text chunks with metadata (`chunk_id`, `chunk_index`, `total_chunks`).
3. **Ingestion Engine** ([`src/core/ingestion/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/ingestion)): Unified orchestrator coordinating file loading, vector eviction, text chunking, and state persistence into atomic execution cycles.

---

## Detailed Component Breakdown & Sub-Guidelines Index

### 1. State Tracker ([`state_tracker.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/state_tracker.py))
- **Detailed Specification**: [📂 `src/core/state_tracker/guidelines.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/guidelines.md)
- **Key Code Elements**:
  - [`FileStatus`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/state_tracker.py#L14-L18): String-backed enumeration (`INDEXED`, `FAILED`, `PENDING`, `EMPTY`).
  - [`FileState`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/state_tracker.py#L21-L30): Dataclass holding hash checksum, file size, modification time, chunk count, and status.
  - [`StateTracker.detect_changes(...)`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/state_tracker/state_tracker.py#L79-L111): Compares disk files against stored JSON state using 64KB chunked SHA-256 hashing.

---

### 2. Text Splitter ([`text_splitter.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/text_splitter/text_splitter.py))
- **Detailed Specification**: [📂 `src/core/text_splitter/guidelines.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/text_splitter/guidelines.md)
- **Key Code Elements**:
  - [`TextSplitter.__init__(...)`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/text_splitter/text_splitter.py#L12-L21): Initializes `RecursiveCharacterTextSplitter` with chunk size 1000 and overlap 150.
  - [`TextSplitter.split_documents(...)`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/text_splitter/text_splitter.py#L23-L44): Generates deterministic chunk IDs (`{hash[:8]}_{section}_chunk_{idx}`) while preserving document metadata.

---

### 3. Ingestion Orchestrator ([`ingestion.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/ingestion/ingestion.py))
- **Detailed Specification**: [📂 `src/core/ingestion/guidelines.md`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/ingestion/guidelines.md)
- **Key Code Elements**:
  - [`IngestionResult`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/ingestion/ingestion.py#L15-L21): Summary dataclass returned by ingestion cycles.
  - [`IngestionEngine.run()`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/core/ingestion/ingestion.py#L39-L100): Executes 4-phase synchronization flow (Change Detection $\rightarrow$ Eviction $\rightarrow$ Parse & Embed $\rightarrow$ State Persistence).
