from pathlib import Path

from src.loaders.base.base import BaseLoader
from src.loaders.docx_loader.docx_loader import DocxLoader
from src.loaders.excel_loader.excel_loader import ExcelCSVLoader
from src.loaders.pdf_loader.pdf_loader import PDFLoader
from src.loaders.text_loader.text_loader import TextLoader


class UnsupportedFormatError(Exception):
    """Raised when an unsupported file format is encountered."""

    pass


class LoaderFactory:
    """Factory class to instantiate appropriate document loader based on file extension."""

    _LOADERS = {
        ".pdf": PDFLoader,
        ".docx": DocxLoader,
        ".xlsx": ExcelCSVLoader,
        ".xls": ExcelCSVLoader,
        ".csv": ExcelCSVLoader,
        ".txt": TextLoader,
        ".md": TextLoader,
    }

    @classmethod
    def get_loader(cls, file_path: Path) -> BaseLoader:
        ext = file_path.suffix.lower()
        loader_cls = cls._LOADERS.get(ext)
        if not loader_cls:
            raise UnsupportedFormatError(
                f"Unsupported file extension '{ext}' for file {file_path.name}"
            )
        return loader_cls()

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        return file_path.suffix.lower() in cls._LOADERS
