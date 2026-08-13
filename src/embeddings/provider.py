from enum import Enum
from typing import Any, Dict, List, Optional

from langchain_core.embeddings import Embeddings

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("embeddings")


class EmbeddingVendor(str, Enum):
    """Supported embedding vendor identifiers."""

    GOOGLE = "google"
    OPENAI = "openai"


VENDOR_MODELS: Dict[EmbeddingVendor, List[Dict[str, Any]]] = {
    EmbeddingVendor.GOOGLE: [
        {
            "name": "gemini-embedding-001",
            "dimension": 1536,
            "description": "Text-only, 100+ languages, MRL support",
        },
        {
            "name": "gemini-embedding-2",
            "dimension": 3072,
            "description": "Multimodal (text, image, video, audio)",
        },
    ],
    EmbeddingVendor.OPENAI: [
        {
            "name": "text-embedding-3-small",
            "dimension": 1536,
            "description": "Cost-effective, general-purpose",
        },
        {
            "name": "text-embedding-3-large",
            "dimension": 3072,
            "description": "High precision, complex domains",
        },
    ],
}

VENDOR_LABELS: Dict[EmbeddingVendor, str] = {
    EmbeddingVendor.GOOGLE: "Google Gemini",
    EmbeddingVendor.OPENAI: "OpenAI",
}


_embedding_instance: Optional[Embeddings] = None
_current_vendor: Optional[EmbeddingVendor] = None
_current_model: Optional[str] = None


def get_default_model(vendor: EmbeddingVendor) -> str:
    """Returns the first model in the registry as the default for a vendor."""
    return VENDOR_MODELS[vendor][0]["name"]


def get_model_dimension(vendor: EmbeddingVendor, model_name: str) -> int:
    """Looks up the default output dimension for a vendor + model combination."""
    for model_info in VENDOR_MODELS[vendor]:
        if model_info["name"] == model_name:
            return model_info["dimension"]
    return 1536


def get_model_names(vendor: EmbeddingVendor) -> List[str]:
    """Returns the list of available model names for a vendor (for sidebar dropdowns)."""
    return [m["name"] for m in VENDOR_MODELS[vendor]]


def get_embedding_function(
    vendor: Optional[EmbeddingVendor] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    dimension: Optional[int] = None,
) -> Embeddings:
    """
    Returns a singleton LangChain Embeddings instance for the given vendor and model.

    On first call, creates the embedding object and caches it at module level.
    On subsequent calls, returns the cached instance if the vendor + model have not
    changed.  Pass a different vendor/model to create a new instance (the old one
    is discarded).

    Args:
        vendor:     The embedding vendor (defaults to settings.EMBEDDING_VENDOR).
        model_name: Model identifier (defaults to the vendor's first registered model).
        api_key:    Override API key (defaults to the relevant key in settings).
        dimension:  Override output dimension (defaults to registry lookup).

    Returns:
        A ready-to-use LangChain ``Embeddings`` instance.
    """
    global _embedding_instance, _current_vendor, _current_model

    resolved_vendor = vendor or EmbeddingVendor(settings.EMBEDDING_VENDOR)
    resolved_model = model_name or get_default_model(resolved_vendor)

    if (
        _embedding_instance is not None
        and _current_vendor == resolved_vendor
        and _current_model == resolved_model
    ):
        return _embedding_instance

    resolved_dimension = dimension or get_model_dimension(resolved_vendor, resolved_model)

    if resolved_vendor == EmbeddingVendor.GOOGLE:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        goog_model = resolved_model
        if not goog_model.startswith("models/"):
            goog_model = f"models/{goog_model}"

        _embedding_instance = GoogleGenerativeAIEmbeddings(
            model=goog_model,
            google_api_key=api_key or settings.GOOGLE_API_KEY or None,
            output_dimensionality=resolved_dimension,
        )

    elif resolved_vendor == EmbeddingVendor.OPENAI:
        from langchain_openai import OpenAIEmbeddings

        _embedding_instance = OpenAIEmbeddings(
            model=resolved_model,
            openai_api_key=api_key or settings.OPENAI_API_KEY or None,
            dimensions=resolved_dimension,
        )

    else:
        raise ValueError(
            f"Unsupported embedding vendor: '{resolved_vendor}'. "
            f"Supported vendors: {[v.value for v in EmbeddingVendor]}"
        )

    _current_vendor = resolved_vendor
    _current_model = resolved_model
    logger.info(
        f"Created {resolved_vendor.value} embedding instance: "
        f"model={resolved_model}, dimension={resolved_dimension}"
    )
    return _embedding_instance


def reset_embedding_instance() -> None:
    """
    Clears the cached singleton embedding instance.

    Call this before ``get_embedding_function()`` when switching vendors so
    that a fresh instance is created on the next call.
    """
    global _embedding_instance, _current_vendor, _current_model
    _embedding_instance = None
    _current_vendor = None
    _current_model = None
    logger.info("Reset embedding singleton instance.")


def get_current_vendor() -> Optional[EmbeddingVendor]:
    """Returns the vendor of the currently cached embedding instance, or None."""
    return _current_vendor


def get_current_model() -> Optional[str]:
    """Returns the model name of the currently cached embedding instance, or None."""
    return _current_model
