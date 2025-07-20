from typing import Literal, Annotated
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Embedding service specific configurations
class DashScopeEmbeddingConfig(BaseSettings):
    """DashScope embedding service specific configuration"""
    type: Literal["dashscope"] = "dashscope"
    api_key: str
    model: str = "text-embedding-v3"
    
    model_config = SettingsConfigDict(env_prefix='EMBEDDING_DASHSCOPE_')


class OpenAIEmbeddingConfig(BaseSettings):
    """OpenAI embedding service specific configuration"""
    type: Literal["openai"] = "openai"
    api_key: str
    model: str = "text-embedding-ada-002"
    
    model_config = SettingsConfigDict(env_prefix='EMBEDDING_OPENAI_')


class CohereEmbeddingConfig(BaseSettings):
    """Cohere embedding service specific configuration"""
    type: Literal["cohere"] = "cohere"
    api_key: str
    model: str = "embed-english-v3.0"
    
    model_config = SettingsConfigDict(env_prefix='EMBEDDING_COHERE_')


class HuggingFaceEmbeddingConfig(BaseSettings):
    """HuggingFace embedding service specific configuration"""
    type: Literal["huggingface"] = "huggingface"
    model: str = "sentence-transformers/all-mpnet-base-v2"
    
    model_config = SettingsConfigDict(env_prefix='EMBEDDING_HUGGINGFACE_')


# Discriminated union for embedding configurations
EmbeddingConfigUnion = Annotated[
    DashScopeEmbeddingConfig | OpenAIEmbeddingConfig | CohereEmbeddingConfig | HuggingFaceEmbeddingConfig,
    Field(discriminator='type')
]


class EmbeddingConfig(BaseSettings):
    """Configuration for embedding service"""
    config: EmbeddingConfigUnion
    
    model_config = SettingsConfigDict(
        env_prefix='EMBEDDING_',
        env_nested_delimiter='_'
    )
