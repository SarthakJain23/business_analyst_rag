from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.config import settings
from src.loaders.base import RawDocument


@dataclass
class DocumentChunk:
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TextSplitter:
    """Recursively splits RawDocument objects into DocumentChunk instances."""

    def __init__(
        self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", " ", ""]

    def _split_text(self, text: str) -> List[str]:
        """Recursive chunk splitting logic."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        # Find suitable separator
        separator = ""
        for s in self.separators:
            if s in text:
                separator = s
                break

        splits = text.split(separator) if separator else list(text)
        current_chunk = []
        current_length = 0

        for split in splits:
            split_len = len(split) + (len(separator) if current_chunk else 0)
            if current_length + split_len > self.chunk_size and current_chunk:
                joined = separator.join(current_chunk)
                if joined.strip():
                    chunks.append(joined.strip())
                # Handle overlap
                overlap_len = 0
                overlap_splits = []
                for item in reversed(current_chunk):
                    if overlap_len + len(item) <= self.chunk_overlap:
                        overlap_splits.insert(0, item)
                        overlap_len += len(item)
                    else:
                        break
                current_chunk = overlap_splits
                current_length = sum(len(x) for x in current_chunk)

            current_chunk.append(split)
            current_length += len(split)

        if current_chunk:
            joined = separator.join(current_chunk)
            if joined.strip():
                chunks.append(joined.strip())

        return chunks

    def split_documents(self, documents: List[RawDocument]) -> List[DocumentChunk]:
        """Splits a list of RawDocuments into DocumentChunks carrying rich metadata."""
        all_chunks: List[DocumentChunk] = []

        for doc in documents:
            text_splits = self._split_text(doc.content)
            file_hash = doc.metadata.get("file_hash", "nohash")[:8]
            page_sec = doc.metadata.get("page_or_section", "sec")
            clean_sec = "".join(c for c in str(page_sec) if c.isalnum() or c in ("_", "-"))

            for idx, split_text in enumerate(text_splits):
                chunk_id = f"{file_hash}_{clean_sec}_chunk_{idx}"
                chunk_metadata = dict(doc.metadata)
                chunk_metadata.update(
                    {
                        "chunk_id": chunk_id,
                        "chunk_index": idx,
                        "total_chunks": len(text_splits),
                    }
                )
                all_chunks.append(
                    DocumentChunk(chunk_id=chunk_id, content=split_text, metadata=chunk_metadata)
                )

        return all_chunks
