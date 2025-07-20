#!/usr/bin/env python3
"""
OceanBase Vector Store Factory Example

This example demonstrates how to use OceanBase vector store through the factory system.
"""

import os
from dotenv import load_dotenv
from langchain_core.documents import Document

from config.settings import Settings
from core.factories.service import ServiceFactory

# Load environment variables
load_dotenv()

def main():
    """
    Example usage of OceanBase vector store through the factory system.
    """
    
    # Load configuration from environment
    settings = Settings()
    
    # Ensure we're using OceanBase
    if settings.vector_store.config.type != "oceanbase":
        print("This example requires OceanBase vector store configuration.")
        print("Set VECTOR_STORE_TYPE=oceanbase in your .env file")
        return
    
    print("=== OceanBase Vector Store Factory Example ===")
    print(f"Configuration: {settings.vector_store.config.type}")
    print(f"Host: {settings.vector_store.config.host}:{settings.vector_store.config.port}")
    print(f"Database: {settings.vector_store.config.db_name}")
    print(f"Table: {settings.vector_store.config.table_name}")
    print()
    
    # Create sample documents
    sample_documents = [
        Document(
            page_content="Python is a high-level programming language known for its simplicity and readability.",
            metadata={"source": "python_intro.md", "category": "programming"}
        ),
        Document(
            page_content="Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            metadata={"source": "ml_basics.md", "category": "ai"}
        ),
        Document(
            page_content="Vector databases are specialized databases for storing and querying high-dimensional vectors.",
            metadata={"source": "vector_db.md", "category": "database"}
        )
    ]
    
    try:
        # Create complete setup using factory
        print("Creating embedding service, vector store, and database session...")
        vector_store = ServiceFactory.create_vector_store(
            settings.embedding,
            settings.vector_store
        )
        db_session = ServiceFactory.create_db_session(
            settings.metadata_db
        )
        
        print("✅ Successfully created all components!")
        print()
        
        # Add documents to vector store
        print("Adding sample documents to vector store...")
        doc_ids = vector_store.add_documents(sample_documents)
        print(f"✅ Added {len(doc_ids)} documents with IDs: {doc_ids}")
        print()
        
        # Search for similar documents
        query = "What is machine learning?"
        print(f"Searching for: '{query}'")
        results = vector_store.similarity_search(query, k=2)
        
        print(f"✅ Found {len(results)} similar documents:")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.page_content[:100]}...")
            print(f"     Source: {doc.metadata.get('source', 'Unknown')}")
        print()
        
        # Search with scores
        print("Searching with similarity scores...")
        scored_results = vector_store.similarity_search_with_score(query, k=2)
        
        print(f"✅ Results with scores:")
        for i, (doc, score) in enumerate(scored_results, 1):
            print(f"  {i}. Score: {score:.4f}")
            print(f"     Content: {doc.page_content[:80]}...")
            print(f"     Source: {doc.metadata.get('source', 'Unknown')}")
        print()
        
        print("=== Example completed successfully! ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure OceanBase is running and configuration is correct.")
    
    finally:
        # Close database session
        if 'db_session' in locals():
            db_session.close()
            print("Database session closed.")

if __name__ == "__main__":
    main()
