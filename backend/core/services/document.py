"""
Document Service

This service handles document loading, processing, and storage operations.
It provides a unified interface for working with different document types (md, txt, pdf).
"""

import glob
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from langchain.vectorstores.base import VectorStore
from langchain_core.documents import Document
from sqlalchemy.orm import Session

from core.factories.document import DocumentLoaderFactory, DocumentSplitterFactory
from core.factories.service import ServiceFactory
from .summary import SummaryService

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Document processing service supporting md, txt, pdf files.
    
    This service provides a unified interface for:
    - Loading documents from files or directories
    - Splitting documents into chunks
    - Embedding and storing documents in vector store
    - Managing document metadata
    """
    
    def __init__(self, settings, db_router):
        """
        Initialize document service with configuration and database router.
        
        Args:
            settings: Application settings containing all configurations
            db_router: DatabaseRouter instance for multi-tenant database access
        """
        self.settings = settings
        self.db_router = db_router
        self._vector_store: Optional[VectorStore] = None
        self._summary_service: Optional[SummaryService] = None
    
    def _initialize_vector_store(self, table_name: str, user_id: Optional[str] = None):
        """Initialize vector store if not already initialized

        Args:
            table_name: Table name for the vector store
            user_id: Optional user ID for user-specific database selection
        """
        if self._vector_store is None:
            print("Initializing vector store...")
            self._vector_store = ServiceFactory.create_vector_store(
                self.settings.embedding,
                self.settings.vector_store,
                table_name,
                user_id=user_id,
                db_router=self.db_router
            )
            print(f"✅ Vector store initialized successfully for table: {table_name}")
    
    def _initialize_summary_service(self):
        """Initialize summary service if not already initialized"""
        if self._summary_service is None:
            print("Initializing summary service...")
            self._summary_service = SummaryService(self.settings)
            print("✅ Summary service initialized successfully")
    
    def embed_and_store(self, documents: List[Document], table_name: str, drop_old: bool = False, user_id: Optional[str] = None) -> bool:
        """
        Embed documents and store them in vector store.

        Args:
            documents: List of documents to embed and store
            table_name: Table name for the vector store
            drop_old: Whether to drop existing data before storing
            user_id: Optional user ID for user-specific database selection

        Returns:
            True if successful, False otherwise
        """
        if not documents:
            print("❌ No documents to embed and store")
            return False

        try:
            # Initialize vector store with dynamic table name
            self._initialize_vector_store(table_name, user_id)
            
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
        table_name: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> List[Document]:
        """
        Search for documents similar to the query.

        Args:
            query: Search query
            table_name: Table name for the vector store
            k: Number of results to return
            filter: Optional filter to apply
            user_id: Optional user ID for user-specific database selection

        Returns:
            List of similar documents
        """
        try:
            # Ensure components are initialized
            self._initialize_vector_store(table_name, user_id)
            
            print(f"Searching for documents similar to: '{query}'")
            
            results = self._vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            
            print(f"✅ Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}")
            return []

    def search_with_summary(
        self,
        query: str,
        table_name: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents and generate a summary of the results.

        Args:
            query: Search query string
            table_name: Table name for the vector store
            k: Number of documents to retrieve
            filter: Optional filter to apply to search
            user_id: Optional user ID for user-specific database selection

        Returns:
            Dictionary containing search results and summary
        """
        try:
            # First, perform the search
            documents = self.search_documents(query, table_name, k, filter, user_id)
            
            if not documents:
                return {
                    "query": query,
                    "documents": [],
                    "summary": "No documents found for the given query.",
                    "document_count": 0
                }
            
            # Initialize summary service and generate summary
            self._initialize_summary_service()
            summary = self._summary_service.summarize_search_results(documents, query)
            
            return {
                "query": query,
                "documents": [{
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in documents],
                "summary": summary,
                "document_count": len(documents)
            }
            
        except Exception as e:
            error_msg = f"Error searching with summary: {e}"
            print(f"❌ {error_msg}")
            return {
                "query": query,
                "documents": [],
                "summary": error_msg,
                "document_count": 0
            }
