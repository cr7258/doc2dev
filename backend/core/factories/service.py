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
    def create_vector_store(
        embedding_config: EmbeddingConfig,
        vector_store_config: VectorStoreConfig,
        table_name: str
    ) -> VectorStore:
        """
        Create vector store with embedding service.
        
        Args:
            embedding_config: Embedding service configuration
            vector_store_config: Vector store configuration
            table_name: Table name for the vector store
            
        Returns:
            VectorStore instance
        """
        # Step 1: Create embedding service
        embeddings = EmbeddingFactory.create_embeddings(embedding_config)
        
        # Step 2: Create vector store with embeddings
        vector_store = VectorStoreFactory.create_vector_store(vector_store_config, embeddings, table_name)
        
        return vector_store
    
    @staticmethod
    def create_db_session(metadata_db_config: MetadataDBConfig) -> Session:
        """
        Create metadata database session.
        
        Args:
            metadata_db_config: Metadata database configuration
            
        Returns:
            SQLAlchemy Session instance
        """
        return MetadataDBFactory.create_session(metadata_db_config)
    