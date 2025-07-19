from typing import Optional, Literal, Annotated
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Metadata database specific configurations
class MySQLMetadataDBConfig(BaseSettings):
    """MySQL metadata database specific configuration"""
    type: Literal["mysql"] = "mysql"
    host: str = "localhost"
    port: int = 3306
    database: str
    username: str
    password: str
    charset: str = "utf8mb4"
    
    model_config = SettingsConfigDict(env_prefix='METADATA_MYSQL_')


class PostgreSQLMetadataDBConfig(BaseSettings):
    """PostgreSQL metadata database specific configuration"""
    type: Literal["postgresql"] = "postgresql"
    host: str = "localhost"
    port: int = 5432
    database: str
    username: str
    password: str
    schema: str = "public"
    
    model_config = SettingsConfigDict(env_prefix='METADATA_POSTGRESQL_')


# Discriminated union for metadata database configurations
MetadataDBConfigUnion = Annotated[
    MySQLMetadataDBConfig | PostgreSQLMetadataDBConfig,
    Field(discriminator='type')
]


class MetadataDBConfig(BaseSettings):
    """Configuration for metadata database"""
    config: MetadataDBConfigUnion
    
    model_config = SettingsConfigDict(env_prefix='METADATA_')
