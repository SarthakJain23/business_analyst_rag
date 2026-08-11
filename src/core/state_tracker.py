import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("state_tracker")


@dataclass
class FileState:
    file_path: str
    file_name: str
    file_hash: str
    file_size_bytes: int
    last_modified: float
    chunk_count: int = 0
    status: str = "indexed"  # "indexed", "failed", "pending"


class StateTracker:
    """Manages hash-based incremental ingestion state in JSON."""

    def __init__(self, metadata_dir: Path = settings.METADATA_DIR):
        self.state_file = metadata_dir / "ingestion_state.json"
        self._state: Dict[str, FileState] = {}
        self.load_state()

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculates SHA-256 hash of a file on disk."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def load_state(self) -> None:
        """Loads recorded file ingestion state from JSON."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self._state = {path: FileState(**data) for path, data in raw_data.items()}
                logger.info(f"Loaded state tracker with {len(self._state)} recorded files.")
            except Exception as e:
                logger.error(f"Failed to read state tracker file {self.state_file}: {e}")
                self._state = {}
        else:
            self._state = {}

    def save_state(self) -> None:
        """Saves current state to JSON."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({path: asdict(state) for path, state in self._state.items()}, f, indent=2)
            logger.info("Saved ingestion state tracker.")
        except Exception as e:
            logger.error(f"Failed to save state tracker: {e}")

    def detect_changes(
        self, documents_dir: Path = settings.DOCUMENTS_DIR
    ) -> Tuple[List[Path], List[Path], List[str]]:
        """
        Scans documents_dir and returns:
        - added_or_modified_files: List of Path objects that are new or updated.
        - deleted_file_paths: List of string file paths that were removed from disk.
        """
        current_disk_files: Dict[str, Path] = {}
        for p in documents_dir.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                current_disk_files[str(p.resolve())] = p

        added_or_modified: List[Path] = []
        unchanged: List[str] = []

        # Check existing state against current disk files
        for path_str, file_path in current_disk_files.items():
            current_hash = self.calculate_file_hash(file_path)
            recorded = self._state.get(path_str)

            if not recorded or recorded.file_hash != current_hash:
                added_or_modified.append(file_path)
            else:
                unchanged.append(path_str)

        # Detect deleted files
        recorded_paths = set(self._state.keys())
        current_paths = set(current_disk_files.keys())
        deleted_paths = list(recorded_paths - current_paths)

        logger.info(
            f"State Detection -> Added/Modified: {len(added_or_modified)}, Deleted: {len(deleted_paths)}, Unchanged: {len(unchanged)}"
        )
        return added_or_modified, deleted_paths, unchanged

    def update_file_state(
        self, file_path: Path, file_hash: str, chunk_count: int, status: str = "indexed"
    ) -> None:
        path_str = str(file_path.resolve())
        stat = file_path.stat()
        self._state[path_str] = FileState(
            file_path=path_str,
            file_name=file_path.name,
            file_hash=file_hash,
            file_size_bytes=stat.st_size,
            last_modified=stat.st_mtime,
            chunk_count=chunk_count,
            status=status,
        )

    def remove_file_state(self, path_str: str) -> None:
        if path_str in self._state:
            del self._state[path_str]

    def get_all_states(self) -> Dict[str, FileState]:
        return self._state.copy()
