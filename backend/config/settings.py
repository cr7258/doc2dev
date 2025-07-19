from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import configuration classes from separate modules
from .metadata_db import MetadataDBConfig
from .vector_store import VectorStoreConfig
from .embedding import EmbeddingConfig
from .llm import LLMConfig


class Settings(BaseSettings):
    """Main application settings"""
    # Metadata database configuration
    metadata_db: MetadataDBConfig = Field(default_factory=MetadataDBConfig)
    
    # Vector database configuration
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    
    # Embedding service configuration
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    
    # LLM service configuration
    llm: LLMConfig = Field(default_factory=LLMConfig)
    
    # Application configuration
    app_name: str = "Doc2Dev"
    debug: bool = False
    log_level: str = "INFO"
    
    # API configuration
    api_base_url: str = "http://localhost:8000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        env_nested_delimiter="__"
    )
