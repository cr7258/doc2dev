"""
Service factory for creating complete service instances with all dependencies.
"""

from langchain.vectorstores.base import VectorStore
from langchain.embeddings.base import Embeddings
from sqlalchemy.orm import Session

from config.settings import Settings
from config.vector_store import VectorStoreConfig
from config.embedding import EmbeddingConfig
from config.metadata_db import MetadataDBConfig
from .vector_store import VectorStoreFactory
from .embedding import EmbeddingFactory
from .metadata_db import MetadataDBFactory


class ServiceFactory:
    """Factory for creating complete service instances with all dependencies."""
    
    @staticmethod
    def create_embedding_vector_store_and_db_session(
        embedding_config: EmbeddingConfig,
        vector_store_config: VectorStoreConfig, 
        metadata_db_config: MetadataDBConfig
    ) -> tuple[VectorStore, Session]:
        """
        Create embedding service, vector store, and database session.
        
        Args:
            embedding_config: Embedding service configuration
            vector_store_config: Vector store configuration
            metadata_db_config: Metadata database configuration
            
        Returns:
            Tuple of (VectorStore, Session)
        """
        # Step 1: Create embedding service
        embeddings = EmbeddingFactory.create_embeddings(embedding_config)
        
        # Step 2: Create vector store with embeddings
        vector_store = VectorStoreFactory.create_vector_store(vector_store_config, embeddings)
        
        # Step 3: Create metadata database session
        db_session = MetadataDBFactory.create_session(metadata_db_config)
        
        return vector_store, db_session

