from typing import Optional, Literal, Annotated
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Vector store specific configurations
class OceanBaseVectorConfig(BaseSettings):
    """OceanBase vector database specific configuration"""
    type: Literal["oceanbase"] = "oceanbase"
    host: str = "127.0.0.1"
    port: int = 2881
    user: str = "root@test"
    password: str = ""
    db_name: str = "doc2dev"
    table_name: str = "langchain_vector"
    metric_type: str = "l2"  # Renamed from vidx_metric_type for consistency
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_STORE_OCEANBASE_')


class ChromaVectorConfig(BaseSettings):
    """Chroma vector database specific configuration"""
    type: Literal["chroma"] = "chroma"
    persist_directory: str = "./chroma_db"
    collection_name: str = "doc2dev"
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_STORE_CHROMA_')


class PGVectorConfig(BaseSettings):
    """PostgreSQL with pgvector extension specific configuration"""
    type: Literal["pgvector"] = "pgvector"
    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str = "postgres"
    schema_name: str = "public"
    table_name: str = "langchain_vectors"
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_STORE_PGVECTOR_')


class QdrantVectorConfig(BaseSettings):
    """Qdrant vector database specific configuration"""
    type: Literal["qdrant"] = "qdrant"
    url: str = "http://localhost:6333"
    collection_name: str = "doc2dev"
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_STORE_QDRANT_')


class ElasticsearchVectorConfig(BaseSettings):
    """Elasticsearch vector database specific configuration"""
    type: Literal["elasticsearch"] = "elasticsearch"
    es_url: str = "http://localhost:9200"
    es_user: Optional[str] = None
    es_password: Optional[str] = None
    index_name: str = "doc2dev"
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_STORE_ELASTICSEARCH_')


# Discriminated union for vector store configurations
VectorStoreConfigUnion = Annotated[
    OceanBaseVectorConfig | ChromaVectorConfig | PGVectorConfig | QdrantVectorConfig | ElasticsearchVectorConfig,
    Field(discriminator='type')
]


class VectorStoreConfig(BaseSettings):
    """Configuration for vector database"""
    config: VectorStoreConfigUnion
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_STORE_')
