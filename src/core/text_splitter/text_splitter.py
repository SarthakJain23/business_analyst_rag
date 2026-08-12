from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings


class TextSplitter:
    """Splits LangChain Document objects using RecursiveCharacterTextSplitter."""

    def __init__(
        self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Splits a list of Documents into chunked Documents carrying rich metadata."""
        chunked_docs: List[Document] = []
        for doc in documents:
            splits = self.splitter.split_documents([doc])
            file_hash = str(doc.metadata.get("file_hash", "nohash"))[:8]
            page_sec = doc.metadata.get("page_or_section", "sec")
            clean_sec = "".join(c for c in str(page_sec) if c.isalnum() or c in ("_", "-"))

            for idx, split_doc in enumerate(splits):
                chunk_id = f"{file_hash}_{clean_sec}_chunk_{idx}"
                meta = dict(split_doc.metadata)
                meta.update(
                    {
                        "chunk_id": chunk_id,
                        "chunk_index": idx,
                        "total_chunks": len(splits),
                    }
                )
                chunked_docs.append(Document(page_content=split_doc.page_content, metadata=meta))

        return chunked_docs
