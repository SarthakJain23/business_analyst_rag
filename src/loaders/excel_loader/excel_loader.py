from pathlib import Path
from typing import List

import pandas as pd
from langchain_core.documents import Document

from src.loaders.base.base import BaseLoader
from src.utils.logger import get_logger

logger = get_logger("excel_loader")


class ExcelCSVLoader(BaseLoader):
    """Loader for Excel (.xlsx, .xls) and CSV (.csv) files formatted as markdown tables."""

    def load(self, file_path: Path, file_hash: str) -> List[Document]:
        documents: List[Document] = []
        ext = file_path.suffix.lower()

        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
                df = df.dropna(how="all")
                markdown_table = df.to_markdown(index=False)
                metadata = {
                    "source_file": str(file_path.resolve()),
                    "file_name": file_path.name,
                    "file_type": ".csv",
                    "file_hash": file_hash,
                    "page_or_section": "CSV Data",
                    "row_count": len(df),
                }
                documents.append(Document(page_content=markdown_table, metadata=metadata))
            else:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    df = df.dropna(how="all")
                    if not df.empty:
                        content = f"# Sheet: {sheet_name}\n\n" + df.to_markdown(index=False)
                        metadata = {
                            "source_file": str(file_path.resolve()),
                            "file_name": file_path.name,
                            "file_type": ext,
                            "file_hash": file_hash,
                            "page_or_section": f"Sheet: {sheet_name}",
                            "row_count": len(df),
                        }
                        documents.append(Document(page_content=content, metadata=metadata))

            logger.info(f"Successfully loaded Excel/CSV file: {file_path.name}")
        except Exception as e:
            logger.error(f"Error reading Excel/CSV file {file_path}: {e}")
            raise e

        return documents
