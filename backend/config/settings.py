from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import configuration classes from separate modules
from .metadata_db import MetadataDBConfig
from .vector_store import VectorStoreConfig
from .embedding import EmbeddingConfig


class Settings(BaseSettings):
    """Main application settings"""
    # Metadata database configuration
    metadata_db: MetadataDBConfig = Field(default_factory=MetadataDBConfig)
    
    # Vector database configuration
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    
    # Embedding service configuration
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    
    # Application configuration
    app_name: str = "Doc2Dev"
    debug: bool = False
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        env_nested_delimiter="__"
    )
