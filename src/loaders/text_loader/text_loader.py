from pathlib import Path
from typing import List

from langchain_core.documents import Document

from src.loaders.base.base import BaseLoader
from src.utils.logger import get_logger

logger = get_logger("text_loader")


class TextLoader(BaseLoader):
    """Loader for plain text (.txt) and Markdown (.md) documents."""

    def load(self, file_path: Path, file_hash: str) -> List[Document]:
        documents: List[Document] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()

            if content:
                metadata = {
                    "source_file": str(file_path.resolve()),
                    "file_name": file_path.name,
                    "file_type": file_path.suffix.lower(),
                    "file_hash": file_hash,
                    "page_or_section": "Document Content",
                }
                documents.append(Document(page_content=content, metadata=metadata))

            logger.info(f"Successfully loaded text document: {file_path.name}")
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            raise e

        return documents
