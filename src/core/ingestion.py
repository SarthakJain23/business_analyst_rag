from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from src.config import settings
from src.core.state_tracker import FileStatus, StateTracker
from src.core.text_splitter import TextSplitter
from src.loaders.factory import LoaderFactory
from src.utils.logger import get_logger

if TYPE_CHECKING:
    from src.vector_store.store import VectorStoreManager

logger = get_logger("ingestion_engine")


@dataclass
class IngestionResult:
    added_or_modified_count: int
    deleted_count: int
    processed_chunks: int
    errors: List[str]
    documents_status: Dict[str, Any]


class IngestionEngine:
    """Unified Orchestrator for Document Ingestion and Incremental Vector Indexing."""

    def __init__(
        self,
        documents_dir: Path = settings.DOCUMENTS_DIR,
        state_tracker: StateTracker = None,
        vector_store: "VectorStoreManager" = None,
        text_splitter: TextSplitter = None,
    ):
        from src.vector_store.store import VectorStoreManager

        self.documents_dir = documents_dir
        self.state_tracker = state_tracker or StateTracker()
        self.vector_store = vector_store or VectorStoreManager()
        self.text_splitter = text_splitter or TextSplitter()

    def run(self) -> IngestionResult:
        """Executes full incremental ingestion cycle."""
        logger.info("Starting incremental ingestion cycle...")
        added_modified, deleted_paths, unchanged = self.state_tracker.detect_changes(
            self.documents_dir
        )

        errors: List[str] = []
        total_chunks_added = 0

        for path_str in deleted_paths:
            logger.info(f"Evicting deleted file vectors: {path_str}")
            self.vector_store.delete_by_file_path(path_str)
            self.state_tracker.remove_file_state(path_str)

        for file_path in added_modified:
            path_str = str(file_path.resolve())
            file_hash = self.state_tracker.calculate_file_hash(file_path)

            if not LoaderFactory.is_supported(file_path):
                logger.warning(f"Skipping unsupported file format: {file_path.name}")
                continue

            try:

                self.vector_store.delete_by_file_path(path_str)

                loader = LoaderFactory.get_loader(file_path)
                raw_docs = loader.load(file_path, file_hash)
                chunks = self.text_splitter.split_documents(raw_docs)

                if chunks:
                    added_count = self.vector_store.add_chunks(chunks)
                    total_chunks_added += added_count
                    self.state_tracker.update_file_state(
                        file_path, file_hash, len(chunks), status=FileStatus.INDEXED
                    )
                else:
                    self.state_tracker.update_file_state(
                        file_path, file_hash, 0, status=FileStatus.EMPTY
                    )

            except Exception as e:
                err_msg = f"Failed to ingest file {file_path.name}: {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)
                self.state_tracker.update_file_state(
                    file_path, file_hash, 0, status=f"{FileStatus.FAILED}: {str(e)}"
                )

        self.state_tracker.save_state()

        result = IngestionResult(
            added_or_modified_count=len(added_modified),
            deleted_count=len(deleted_paths),
            processed_chunks=total_chunks_added,
            errors=errors,
            documents_status=self.state_tracker.get_all_states(),
        )

        logger.info(
            f"Ingestion Completed. Chunks added/updated: {total_chunks_added}, Errors: {len(errors)}"
        )
        return result
