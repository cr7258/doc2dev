"""
Metadata database factory for creating database connections based on configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from config.metadata_db import MetadataDBConfig


class MetadataDBFactory:
    """Factory for creating metadata database connections based on configuration."""
    
    @staticmethod
    def create_engine(metadata_db_config: MetadataDBConfig) -> Engine:
        """
        Create a SQLAlchemy engine based on configuration.
        
        Args:
            metadata_db_config: Metadata database configuration
            
        Returns:
            SQLAlchemy Engine instance
            
        Raises:
            ValueError: If database type is not supported
        """
        db_type = metadata_db_config.config.type
        
        match db_type:
            case "mysql":
                connection_string = (
                    f"mysql+pymysql://{metadata_db_config.config.user}:{metadata_db_config.config.password}"
                    f"@{metadata_db_config.config.host}:{metadata_db_config.config.port}/{metadata_db_config.config.database}"
                )
                
                engine_kwargs = {
                    "pool_size": metadata_db_config.config.pool_size,
                    "max_overflow": metadata_db_config.config.max_overflow,
                    "pool_timeout": metadata_db_config.config.pool_timeout,
                    "pool_recycle": metadata_db_config.config.pool_recycle,
                }
                
                return create_engine(connection_string, **engine_kwargs)
            
            case "postgresql":
                connection_string = (
                    f"postgresql+psycopg2://{metadata_db_config.config.user}:{metadata_db_config.config.password}"
                    f"@{metadata_db_config.config.host}:{metadata_db_config.config.port}/{metadata_db_config.config.database}"
                )
                
                engine_kwargs = {
                    "pool_size": metadata_db_config.config.pool_size,
                    "max_overflow": metadata_db_config.config.max_overflow,
                    "pool_timeout": metadata_db_config.config.pool_timeout,
                    "pool_recycle": metadata_db_config.config.pool_recycle,
                }
                
                return create_engine(connection_string, **engine_kwargs)
            
            case _:
                raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def create_session_factory(metadata_db_config: MetadataDBConfig) -> sessionmaker:
        """
        Create a SQLAlchemy session factory based on configuration.
        
        Args:
            metadata_db_config: Metadata database configuration
            
        Returns:
            SQLAlchemy sessionmaker
        """
        engine = MetadataDBFactory.create_engine(metadata_db_config)
        return sessionmaker(bind=engine)
    
    @staticmethod
    def create_session(metadata_db_config: MetadataDBConfig) -> Session:
        """
        Create a SQLAlchemy session based on configuration.
        
        Args:
            metadata_db_config: Metadata database configuration
            
        Returns:
            SQLAlchemy Session instance
        """
        session_factory = MetadataDBFactory.create_session_factory(metadata_db_config)
        return session_factory()
