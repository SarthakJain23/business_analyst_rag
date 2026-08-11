from pathlib import Path
from typing import List

from pypdf import PdfReader

from src.loaders.base import BaseLoader, RawDocument
from src.utils.logger import get_logger

logger = get_logger("pdf_loader")


class PDFLoader(BaseLoader):
    """Loader for PDF documents preserving page metadata."""

    def load(self, file_path: Path, file_hash: str) -> List[RawDocument]:
        documents: List[RawDocument] = []
        try:
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = text.strip()
                if text:
                    metadata = {
                        "source_file": str(file_path.resolve()),
                        "file_name": file_path.name,
                        "file_type": ".pdf",
                        "file_hash": file_hash,
                        "page_or_section": f"Page {idx + 1}",
                        "total_pages": len(reader.pages),
                    }
                    documents.append(RawDocument(content=text, metadata=metadata))
            logger.info(f"Successfully loaded {len(documents)} pages from PDF: {file_path.name}")
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
            raise e

        return documents
