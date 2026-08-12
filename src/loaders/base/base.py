from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from langchain_core.documents import Document


class BaseLoader(ABC):
    """Abstract Base Class for all document loaders returning LangChain Documents."""

    @abstractmethod
    def load(self, file_path: Path, file_hash: str) -> List[Document]:
        """Loads and parses a file into a list of LangChain Document instances."""
        pass
