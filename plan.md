# Doc2Dev Backend Refactoring Plan

## Target Directory Structure

```
/backend/
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration management
│
├── core/
│   ├── __init__.py
│   ├── interfaces.py           # Abstract interfaces for components
│   ├── factories.py            # Factory classes for component creation
│   └── services             # Business logic services
         └── document
         └── vector
         └── metadata
│
├── adapters/
│   ├── __init__.py
│   ├── vector_stores/
│   │   ├── __init__.py
│   │   ├── oceanbase.py        # OceanBase vector store adapter
│   │   ├── chroma.py           # ChromaDB adapter
│   │   └── pgvector.py         # PGVector adapter
│   │
│   ├── metadata/
│   │   ├── __init__.py
│   │   ├── mysql.py            # MySQL metadata adapter
│   │   └── postgresql.py       # PostgreSQL metadata adapter
│   │
│   └── embeddings/
│       ├── __init__.py
│       ├── dashscope.py        # DashScope embedding adapter
│       └── openai.py           # OpenAI embedding adapter
│
├── utils/
│   ├── __init__.py
│   └── markdown.py             # Markdown processing utilities
│
├── api/
│   ├── __init__.py
│   ├── dependencies.py         # FastAPI dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── repositories.py     # Repository endpoints
│   │   └── documents.py        # Document processing endpoints
│   └── models.py               # Pydantic models for API
│
├── mcp/
│   ├── __init__.py
│   ├── server.py               # MCP server implementation
│   └── tools.py                # MCP tools implementation
│
├── main.py                     # FastAPI application entry point
└── requirements.txt            # Project dependencies
```

## Refactoring Steps

### Phase 1: Setup Project Structure

- [] Create the new directory structure
- [] Set up package initialization files
- [] Move existing utility functions to appropriate locations

### Phase 2: Core Implementation

- [] Implement core interfaces in `core/interfaces.py`
- [] Create factory classes in `core/factories.py`
- [] Implement configuration management in `config/settings.py`

### Phase 3: Adapter Implementation

- [] Implement OceanBase vector store adapter
- [] Implement MySQL metadata database adapter
- [] Implement DashScope embedding adapter
- [] (Optional) Implement additional adapters for other providers

## Implementation Details

### Core Components

The system will leverage LangChain's existing abstractions for vector stores and embeddings, and will have a custom interface for metadata database operations:

1. **Vector Stores**
   - Use LangChain's `VectorStore` interface from `langchain_core.vectorstores`
   - Examples: `OceanbaseVectorStore`, `Chroma`, `PGVector`
   - Factory pattern to create instances based on configuration

   Example code:
   ```python
   from typing import List, Dict, Any, Optional
   from langchain_core.vectorstores import VectorStore
   from langchain_core.documents import Document
   from langchain_oceanbase.vectorstores import OceanbaseVectorStore
   
   # Factory class
   class VectorStoreFactory:
       @staticmethod
       def create(embedding_function, config) -> VectorStore:
           """Create a vector store instance based on configuration
           
           Args:
               embedding_function: Embedding function to use
               config: Vector store configuration
               
           Returns:
               VectorStore instance
           """
           provider = config["provider"]
           
           if provider == "oceanbase":
               return OceanbaseVectorStore(
                   embedding_function=embedding_function,
                   table_name=config["table_name"],
                   connection_args=config["connection_args"],
                   vidx_metric_type="l2"
               )
           # Add more providers as needed
           else:
               raise ValueError(f"Unsupported vector store provider: {provider}")
       
       @staticmethod
       def delete(table_name: str, connection_args: Dict[str, Any], provider: str = "oceanbase") -> bool:
           """Delete a vector table
            
           Args:
               table_name: Name of the vector table to delete
               connection_args: Connection arguments for the database
               provider: Vector store provider (default: "oceanbase")
                
           Returns:
               bool: Whether the deletion was successful
           """
           try:
               if provider == "oceanbase":
                   # Connect to OceanBase
                   import pymysql
                   connection = pymysql.connect(**connection_args)
                   
                   with connection.cursor() as cursor:
                       # Drop the vector table
                       sql = f"DROP TABLE IF EXISTS {table_name}"
                       cursor.execute(sql)
                       connection.commit()
                   return True
               # Add more providers as needed
               else:
                   raise ValueError(f"Unsupported vector store provider for deletion: {provider}")
           except Exception as e:
               print(f"Failed to delete vector table: {str(e)}")
               return False
           finally:
               if 'connection' in locals() and connection:
                   connection.close()
   
   # Example usage in a service class
   class VectorService:
       def __init__(self, vector_store: VectorStore):
           self.vector_store = vector_store
       
       def similarity_search(self, query: str, k: int = 4, filter: Optional[Dict] = None, **kwargs: Any) -> List[Document]:
           """Search for documents similar to the query
           
           Args:
               query: Query string
               k: Number of documents to return
               filter: Optional filter for document metadata
               **kwargs: Additional keyword arguments to pass to the vector store
               
           Returns:
               List of similar documents
           """
           return self.vector_store.similarity_search(
               query=query,
               k=k,
               filter=filter,
               **kwargs
           )
       
       def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
           """Add documents to the vector store
           
           Args:
               documents: List of documents to add
               **kwargs: Additional keyword arguments to pass to the vector store
               
           Returns:
               List of document IDs
           """
           return self.vector_store.add_documents(documents, **kwargs)
   ```

2. **Embeddings**
   - Use LangChain's `Embeddings` interface from `langchain_core.embeddings`
   - Examples: `DashScopeEmbeddings`, `OpenAIEmbeddings`
   - Factory pattern to create instances based on configuration

   Example code:
   ```python
   from langchain_core.embeddings import Embeddings
   from langchain_community.embeddings import DashScopeEmbeddings, OpenAIEmbeddings
   
   # Factory class
   class EmbeddingFactory:
       @staticmethod
       def create(config) -> Embeddings:
           provider = config["provider"]
           
           if provider == "dashscope":
               return DashScopeEmbeddings(
                   model=config["model"],
               )
           elif provider == "openai":
               return OpenAIEmbeddings(
                   model=config["model"],
               )
           # Add more providers as needed
           else:
               raise ValueError(f"Unsupported embedding provider: {provider}")
   ```

3. **MetadataDBInterface**
   - `get_db_connection()`: Get database connection
   - `get_repository(field=None, value=None)`: Get repository, returns all if field is None, or filtered by field/value if specified
   - `add_repository(repository)`: Add a new repository using a Repository object
   - `update_repository(repository)`: Update repository using a Repository object
   - `delete_repository(id)`: Delete a repository

   Example code:
   ```python
   from typing import List, Dict, Any, Optional
   from dataclasses import dataclass, asdict, fields
   from datetime import datetime
   import json
   import pymysql
   from pymysql.cursors import DictCursor
   
   @dataclass
   class Repository:
       """Repository data model"""
       name: str
       repo: str
       repo_url: str
       description: str = ''
       repo_status: str = 'pending'
       tokens: int = 0
       snippets: int = 0
       id: Optional[int] = None
       created_at: Optional[datetime] = None
       updated_at: Optional[datetime] = None
   
   # OceanBase connection parameters
   DB_CONNECTION_ARGS = {
       "host": "127.0.0.1",
       "port": 2881,
       "user": "root@test",
       "password": "admin",
       "database": "doc2dev",
       "charset": "utf8mb4"
   }
   
   def get_db_connection():
       """Get database connection"""
       try:
           connection = pymysql.connect(**DB_CONNECTION_ARGS)
           return connection
       except Exception as e:
           print(f"Database connection failed: {str(e)}")
           raise
   
   def get_repositories(field=None, value=None) -> List[Dict[str, Any]]:
        """Get repositories, with optional filtering
        
        Args:
            field: Optional database field to filter on ('name', 'repo', or 'id')
                  If None, returns all repositories
            value: Value to filter by, required if field is specified
            
        Returns:
            List[Dict]: List of repository information dictionaries
                       Returns a single-item list if field is specified and found
                       Returns empty list if no matches or on error
        """
        try:
            connection = get_db_connection()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Base SQL query
                sql = """
                SELECT id, name, description, repo, repo_url, 
                       tokens, snippets, repo_status, created_at, updated_at
                FROM repositories
                """
                
                # Determine if we're getting all repositories or filtering
                if field is not None:
                    # Validate field
                    valid_fields = ['name', 'repo', 'id']
                    if field not in valid_fields:
                        raise ValueError(f"Invalid field: {field}. Must be one of {valid_fields}")
                    
                    # Add WHERE clause for filtering
                    sql += f"WHERE {field} = %s"
                    cursor.execute(sql, (value,))
                    
                    # For single item queries, wrap result in a list for consistent return type
                    result = cursor.fetchone()
                    return [result] if result else []
                else:
                    # Get all repositories
                    sql += "ORDER BY name"
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Failed to get repositories: {str(e)}")
            return []
        finally:
            if connection:
                connection.close()
   
   def add_repository(repository: Repository) -> bool:
        """Add a new repository using a Repository object
        
        Args:
            repository: Repository object containing repository information
            
        Returns:
            bool: Whether the addition was successful
        """
        try:
            # Convert Repository object to dictionary
            data = asdict(repository)
            
            # Verify required fields
            required_fields = ['name', 'repo', 'repo_url']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Missing required field: {field}")
                    
            # Remove id, created_at, updated_at if present
            for field in ['id', 'created_at', 'updated_at']:
                if field in data:
                    del data[field]
            
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # Dynamically build SQL insert statement
                fields_str = ", ".join(data.keys())
                placeholders = ", ".join(["%s"] * len(data))
                
                sql = f"""
                INSERT INTO repositories ({fields_str})
                VALUES ({placeholders})
                """
                
                # Execute insert
                cursor.execute(sql, tuple(data.values()))
                connection.commit()
                return True
        except Exception as e:
            print(f"Failed to add repository: {str(e)}")
            return False
        finally:
            if connection:
                connection.close()
   
   def update_repository(repository: Repository) -> bool:
        """Update repository using a Repository object
        
        Args:
            repository: Repository object containing updated information
            
        Returns:
            bool: Whether the update was successful
        """
        try:
            # Ensure repository has an ID
            if repository.id is None:
                raise ValueError("Repository ID is required for update")
                
            # Convert to dictionary and filter fields
            data = asdict(repository)
            valid_fields = ['name', 'description', 'repo', 'repo_url', 'repo_status', 'tokens', 'snippets']
            update_fields = {k: v for k, v in data.items() if k in valid_fields}
            
            # Ensure we have fields to update
            if not update_fields:
                raise ValueError("No valid fields provided for update")
                
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # Dynamically build SQL update statement
                set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
                sql = f"""
                UPDATE repositories
                SET {set_clause}
                WHERE id = %s
                """
                
                # Create parameter tuple with values in the same order as fields in SQL
                params = tuple(update_fields.values()) + (repository.id,)
                
                # Execute update
                cursor.execute(sql, params)
                connection.commit()
                return True
        except Exception as e:
            print(f"Failed to update repository: {str(e)}")
            return False
        finally:
            if connection:
                connection.close()
   ```

### Usage Example

In a FastAPI application, the same concept would be implemented as dependencies that are injected into the API endpoints:

```python
# In FastAPI application

# Create singleton instances using lifespan context manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load config and create resources
    app.state.config = load_config()
    app.state.embedding_model = EmbeddingFactory.create(app.state.config["embedding"])
    
    # Initialize vector store once
    app.state.vector_store = VectorStoreFactory.create(
        app.state.embedding_model, 
        app.state.config["vector_store"]
    )
    
    # Initialize vector service once
    app.state.vector_service = VectorService(app.state.vector_store)
    
    yield  # This is where the app runs and handles requests
    
    # Shutdown: clean up resources if needed
    app.state.vector_service = None
    app.state.vector_store = None
    app.state.embedding_model = None

# Pass the lifespan to FastAPI
app = FastAPI(lifespan=lifespan)

# Dependency function
def get_vector_service(request: Request):
    # Simply return the pre-initialized vector service
    return request.app.state.vector_service

# API endpoint using the dependency
@app.post("/search")
async def search_documents(query: str, service: VectorService = Depends(get_vector_service)):
    return service.similarity_search(query)
```

This approach leverages FastAPI's dependency injection system and creates singleton instances at application startup for resources that can be shared across requests.

### Configuration System

The configuration system will allow users to specify:

1. Which vector database to use
2. Which metadata database to use
3. Which embedding API to use
4. Connection parameters for each component

Example configuration (config.yaml):

```yaml
vector_store:
  provider: oceanbase
  connection_args:
    host: 127.0.0.1
    port: 2881
    user: root@test
    password: admin
    db_name: doc2dev
  table_name: langchain_vector

embedding:
  provider: dashscope
  model: text-embedding-v3
  api_key: your-api-key

metadata_db:
  provider: mysql
  connection_args:
    host: 127.0.0.1
    port: 2881
    user: root@test
    password: admin
    database: doc2dev
```

This refactoring will make the system more modular and flexible, allowing users to easily switch between different vector databases, metadata databases, and embedding APIs based on their needs.
