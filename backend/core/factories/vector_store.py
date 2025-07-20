"""
Vector store factory for creating vector store instances based on configuration.
"""

from typing import Optional
from langchain.vectorstores.base import VectorStore
from langchain.embeddings.base import Embeddings

# Vector store imports
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.vectorstores import Qdrant
from langchain_community.vectorstores import ElasticsearchStore

from config.vector_store import VectorStoreConfig


class VectorStoreFactory:
    """Factory for creating vector store instances based on configuration."""
    
    @staticmethod
    def create_vector_store(vector_store_config: VectorStoreConfig, embeddings: Embeddings, table_name: str) -> VectorStore:
        """
        Create a vector store instance based on configuration.
        
        Args:
            vector_store_config: Vector store configuration
            embeddings: Embedding model instance
            table_name: Table name for the vector store
            
        Returns:
            VectorStore instance
            
        Raises:
            ValueError: If vector store type is not supported
        """
        store_type = vector_store_config.config.type
        
        match store_type:
            case "oceanbase":
                # Direct use of LangChain OceanBase implementation
                try:
                    from langchain_oceanbase.vectorstores import OceanbaseVectorStore
                    return OceanbaseVectorStore(
                        embedding_function=embeddings,
                        table_name=table_name.replace('-', '_'),  # Ensure string type and sanitize table name
                        connection_args={
                            "host": vector_store_config.config.host,
                            "port": str(vector_store_config.config.port),
                            "user": vector_store_config.config.user,
                            "password": vector_store_config.config.password,
                            "db_name": vector_store_config.config.db_name,
                        },
                    )
                except ImportError:
                    raise ImportError(
                        "OceanBase vector store requires 'langchain-oceanbase' package. "
                        "Install it with: pip install langchain-oceanbase"
                    )
            
            case "chroma":
                return Chroma(
                    embedding_function=embeddings,
                    persist_directory=vector_store_config.config.persist_directory,
                    collection_name=vector_store_config.config.collection_name,
                )
            
            case "pgvector":
                return PGVector(
                    embedding_function=embeddings,
                    connection_string=vector_store_config.config.connection_string,
                    collection_name=vector_store_config.config.collection_name,
                    distance_strategy=vector_store_config.config.distance_strategy,
                )
            
            case "qdrant":
                return Qdrant(
                    client=None,  # Will be created from config
                    collection_name=vector_store_config.config.collection_name,
                    embeddings=embeddings,
                    url=vector_store_config.config.url,
                    api_key=vector_store_config.config.api_key,
                    distance_strategy=vector_store_config.config.distance_strategy,
                )
            
            case "elasticsearch":
                return ElasticsearchStore(
                    es_url=vector_store_config.config.url,
                    index_name=vector_store_config.config.index_name,
                    embedding=embeddings,
                    es_user=vector_store_config.config.username,
                    es_password=vector_store_config.config.password,
                )
            
            case _:
                raise ValueError(f"Unsupported vector store type: {store_type}")
