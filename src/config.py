import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(BASE_DIR / ".env")


class Settings:
    """Centralized Application Settings."""

    BASE_DIR: Path = BASE_DIR

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    GEMINI_LLM_MODEL: str = "gemini-3.6-flash"

    EMBEDDING_VENDOR: str = os.getenv("EMBEDDING_VENDOR", "google")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    DOCUMENTS_DIR: Path = BASE_DIR / "data/documents"
    VECTOR_STORE_DIR: Path = BASE_DIR / "data/vector_store"
    METADATA_DIR: Path = BASE_DIR / "data/metadata"

    CHROMA_COLLECTION_NAME: str = "business_analyst_documents"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.3

    def ensure_directories(self):
        """Ensures all required local storage directories exist."""
        self.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        self.METADATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
