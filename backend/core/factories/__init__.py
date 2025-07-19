"""
Factory System

This module provides factory classes for creating various components
used in the Doc2Dev system, including vector stores, embeddings,
metadata databases, document processing, and unified services.
"""

from .document import DocumentLoaderFactory, DocumentSplitterFactory
from .embedding import EmbeddingFactory
from .metadata_db import MetadataDBFactory
from .service import ServiceFactory
from .vector_store import VectorStoreFactory

__all__ = [
    "DocumentLoaderFactory",
    "DocumentSplitterFactory",
    "EmbeddingFactory",
    "MetadataDBFactory",
    "ServiceFactory",
    "VectorStoreFactory",
]