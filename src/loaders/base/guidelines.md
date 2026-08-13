# Base Loader Guidelines (`base.py`)

## Folder & File Context

The [`src/loaders/base/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base) directory contains [`base.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py), which defines the abstract base interface [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14).

All concrete file loaders in this application inherit from this abstract class, ensuring a consistent polymorphic interface (`load()`) across different file types.

---

## Detailed Code Explanation & Interface Definition

### Abstract Base Class ([`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14))

```python
class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: Path, file_hash: str) -> List[Document]:
        pass
```

- **`file_path`**: Absolute path to source document on disk.
- **`file_hash`**: Pre-computed SHA-256 hash string for state tracking.
- **Returns**: `List[Document]` (LangChain `Document` objects with `page_content` and metadata dictionary).

---

## Standardized Metadata Schema

All loaders emitting `Document` instances must attach standard keys in `doc.metadata`:
- `source_file`: Resolved absolute file path string.
- `file_name`: Basename of document file.
- `file_type`: Lowercase file extension (e.g. `.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.md`).
- `file_hash`: SHA-256 state hash.
- `page_or_section`: Section label (e.g., `Page 1`, `Sheet: Financials`, `Document Body`).
