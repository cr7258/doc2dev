"""
Embedding factory for creating embedding instances based on configuration.
"""

from langchain.embeddings.base import Embeddings

# Embedding imports
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from config.embedding import EmbeddingConfig


class EmbeddingFactory:
    """Factory for creating embedding instances based on configuration."""
    
    @staticmethod
    def create_embeddings(embedding_config: EmbeddingConfig) -> Embeddings:
        """
        Create an embedding instance based on configuration.
        
        Args:
            embedding_config: Embedding configuration
            
        Returns:
            Embeddings instance
            
        Raises:
            ValueError: If embedding type is not supported
        """
        embedding_type = embedding_config.config.type
        
        match embedding_type:
            case "dashscope":
                return DashScopeEmbeddings(
                    model=embedding_config.config.model,
                    dashscope_api_key=embedding_config.config.api_key,
                )
            
            case "openai":
                return OpenAIEmbeddings(
                    model=embedding_config.config.model,
                    openai_api_key=embedding_config.config.api_key,
                    openai_api_base=embedding_config.config.base_url,
                )
            
            case "cohere":
                return CohereEmbeddings(
                    model=embedding_config.config.model,
                    cohere_api_key=embedding_config.config.api_key,
                )
            
            case "huggingface":
                return HuggingFaceEmbeddings(
                    model_name=embedding_config.config.model_name,
                    cache_folder=embedding_config.config.cache_folder,
                    encode_kwargs=embedding_config.config.encode_kwargs or {},
                )
            
            case _:
                raise ValueError(f"Unsupported embedding type: {embedding_type}")
