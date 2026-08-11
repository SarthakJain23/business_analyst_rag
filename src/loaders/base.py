from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class RawDocument:
    """Standardized document data structure returned by loaders."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def source_file(self) -> str:
        return self.metadata.get("source_file", "")

    @property
    def file_name(self) -> str:
        return self.metadata.get("file_name", "")


class BaseLoader(ABC):
    """Abstract Base Class for all document loaders."""

    @abstractmethod
    def load(self, file_path: Path, file_hash: str) -> List[RawDocument]:
        """Loads and parses a file into a list of RawDocument instances."""
        pass
