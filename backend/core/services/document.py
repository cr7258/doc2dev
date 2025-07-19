"""
Document Service

This service handles document loading, processing, and storage operations.
It provides a unified interface for working with different document types (md, txt, pdf).
"""

import glob
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from langchain.vectorstores.base import VectorStore
from langchain_core.documents import Document
from sqlalchemy.orm import Session

from config.settings import Settings
from core.factories.document import DocumentLoaderFactory, DocumentSplitterFactory
from core.factories.service import ServiceFactory


class DocumentService:
    """
    Document processing service supporting md, txt, pdf files.
    
    This service provides a unified interface for:
    - Loading documents from files or directories
    - Splitting documents into chunks
    - Embedding and storing documents in vector store
    - Managing document metadata
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize document service with configuration.
        
        Args:
            settings: Application settings containing all configurations
        """
        self.settings = settings
        self._vector_store: Optional[VectorStore] = None
        self._db_session: Optional[Session] = None
    
    def _initialize_vector_store_and_db_session(self):
        """Initialize vector store and database session if not already initialized"""
        if self._vector_store is None or self._db_session is None:
            print("Initializing vector store and database session...")
            self._vector_store, self._db_session = ServiceFactory.create_embedding_vector_store_and_db_session(
                self.settings.embedding,
                self.settings.vector_store,
                self.settings.metadata_db
            )
            print("✅ Vector store and database session initialized successfully")
    
    def load_documents(self, path_or_paths: Union[str, List[str]]) -> List[Document]:
        """
        Load documents from files or directories.
        
        Args:
            path_or_paths: Single file path, directory path, or list of file paths
            
        Returns:
            List of loaded Document objects
        """
        print(f"Loading documents from: {path_or_paths}")
        
        documents = []
        files = self._get_supported_files(path_or_paths)
        
        if not files:
            print("❌ No supported files found")
            return documents
        
        print(f"Found {len(files)} supported files")
        
        for file_path in files:
            try:
                file_ext = Path(file_path).suffix.lower().lstrip('.')
                
                # Get LangChain DocumentLoader class
                loader_class = DocumentLoaderFactory.get_loader(file_ext)
                
                # Instantiate and load document
                loader = loader_class(file_path)
                docs = loader.load()
                
                # Add file type metadata
                for doc in docs:
                    doc.metadata.update({
                        'file_type': file_ext,
                        'source_file': file_path,
                        'file_name': Path(file_path).name
                    })
                
                documents.extend(docs)
                print(f"✅ Loaded {len(docs)} documents from {Path(file_path).name}")
                
            except Exception as e:
                print(f"❌ Failed to load {file_path}: {e}")
                continue
        
        print(f"✅ Successfully loaded {len(documents)} documents total")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks based on file type.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        if not documents:
            return []
        
        print(f"Splitting {len(documents)} documents...")
        
        split_docs = []
        
        for doc in documents:
            file_type = doc.metadata.get('file_type', 'text')
            
            try:
                # Get appropriate splitter
                splitter = DocumentSplitterFactory.get_splitter(file_type)
                chunks = splitter.split_documents([doc])
                
                # Add chunk metadata
                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    })
                
                split_docs.extend(chunks)
                print(f"✅ Split {doc.metadata.get('file_name', 'document')} into {len(chunks)} chunks")
                
            except Exception as e:
                print(f"❌ Failed to split document {doc.metadata.get('file_name', 'unknown')}: {e}")
                # If splitting fails, keep original document
                split_docs.append(doc)
        
        print(f"✅ Total chunks created: {len(split_docs)}")
        return split_docs
    
    def embed_and_store(self, documents: List[Document], drop_old: bool = False) -> bool:
        """
        Embed documents and store them in vector store.
        
        Args:
            documents: List of documents to embed and store
            drop_old: Whether to drop existing data before storing
            
        Returns:
            True if successful, False otherwise
        """
        if not documents:
            print("❌ No documents to embed and store")
            return False
        
        try:
            # Ensure components are initialized
            self._initialize_vector_store_and_db_session()
            
            print(f"Embedding and storing {len(documents)} documents...")
            
            # Add documents to vector store
            doc_ids = self._vector_store.add_documents(documents)
            
            print(f"✅ Successfully embedded and stored {len(doc_ids)} documents")
            return True
            
        except Exception as e:
            print(f"❌ Failed to embed and store documents: {e}")
            return False
    
    def search_documents(
        self, 
        query: str, 
        k: int = 5, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional filter to apply
            
        Returns:
            List of similar documents
        """
        try:
            # Ensure components are initialized
            self._initialize_vector_store_and_db_session()
            
            print(f"Searching for documents similar to: '{query}'")
            
            results = self._vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            
            print(f"✅ Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            print(f"❌ Failed to search documents: {e}")
            return []
    
    def search_with_scores(
        self, 
        query: str, 
        k: int = 5, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Search for documents with similarity scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional filter to apply
            
        Returns:
            List of (document, score) tuples
        """
        try:
            # Ensure components are initialized
            self._initialize_vector_store_and_db_session()
            
            print(f"Searching for documents with scores similar to: '{query}'")
            
            results = self._vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            print(f"✅ Found {len(results)} similar documents with scores")
            return results
            
        except Exception as e:
            print(f"❌ Failed to search documents with scores: {e}")
            return []
    
    def process_documents(
        self, 
        path_or_paths: Union[str, List[str]], 
        drop_old: bool = False
    ) -> bool:
        """
        Complete document processing pipeline: load -> split -> embed -> store.
        
        Args:
            path_or_paths: Single file path, directory path, or list of file paths
            drop_old: Whether to drop existing data before storing
            
        Returns:
            True if successful, False otherwise
        """
        print("=== Starting document processing pipeline ===")
        
        try:
            # Step 1: Load documents
            documents = self.load_documents(path_or_paths)
            if not documents:
                return False
            
            # Step 2: Split documents
            split_docs = self.split_documents(documents)
            if not split_docs:
                return False
            
            # Step 3: Embed and store
            success = self.embed_and_store(split_docs, drop_old=drop_old)
            
            if success:
                print("=== Document processing pipeline completed successfully ===")
            else:
                print("=== Document processing pipeline failed ===")
            
            return success
            
        except Exception as e:
            print(f"❌ Document processing pipeline failed: {e}")
            return False
    
    def _get_supported_files(self, path_or_paths: Union[str, List[str]]) -> List[str]:
        """Get all supported files from input paths"""
        supported_extensions = DocumentLoaderFactory.get_supported_extensions()
        files = []
        
        if isinstance(path_or_paths, list):
            # List of file paths
            files = path_or_paths
        elif os.path.isdir(path_or_paths):
            # Directory - scan for supported files
            print(f"Scanning directory: {path_or_paths}")
            for ext in supported_extensions:
                pattern = os.path.join(path_or_paths, f"**/*{ext}")
                files.extend(glob.glob(pattern, recursive=True))
        else:
            # Single file path
            files = [path_or_paths]
        
        # Filter to keep only supported file types
        supported_files = [
            f for f in files 
            if Path(f).suffix.lower() in supported_extensions and os.path.isfile(f)
        ]
        
        return supported_files
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types"""
        return ["md", "txt", "pdf"]
    
    def close(self):
        """Close database session if open"""
        if self._db_session:
            self._db_session.close()
            print("Database session closed")
