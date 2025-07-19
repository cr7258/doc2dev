#!/usr/bin/env python3
"""
Example usage of SummaryService and DocumentService with summarization.

This example demonstrates:
1. Using SummaryService independently
2. Using DocumentService.search_with_summary() for integrated search and summarization
3. Migrating from the old summarize.py approach
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.settings import Settings
from core.services import DocumentService, SummaryService
from langchain_core.documents import Document


def example_summary_service_usage():
    """Example of using SummaryService independently"""
    print("=== SummaryService Independent Usage ===")
    
    # Load settings
    settings = Settings()
    
    # Create summary service
    summary_service = SummaryService(settings)
    
    # Create sample documents
    sample_documents = [
        Document(
            page_content="Python is a high-level programming language. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            metadata={"source": "python_intro.md", "category": "programming"}
        ),
        Document(
            page_content="FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.",
            metadata={"source": "fastapi_docs.md", "category": "web_framework"}
        ),
        Document(
            page_content="LangChain is a framework for developing applications powered by language models. It provides tools for document loading, text splitting, and vector stores.",
            metadata={"source": "langchain_guide.md", "category": "ai_framework"}
        )
    ]
    
    # Generate summary
    query = "Python web development frameworks"
    summary = summary_service.summarize_search_results(sample_documents, query)
    
    print(f"Query: {query}")
    print(f"Summary:\n{summary}")
    print()
    
    # Service cleanup is automatic


def example_document_service_with_summary():
    """Example of using DocumentService with integrated summarization"""
    print("=== DocumentService with Integrated Summarization ===")
    
    # Load settings
    settings = Settings()
    
    # Create document service
    doc_service = DocumentService(settings)
    
    try:
        # Note: This assumes you have documents already embedded in your vector store
        # For a real example, you would first need to:
        # 1. Load documents: documents = doc_service.load_documents("path/to/docs")
        # 2. Embed and store: doc_service.embed_and_store(documents)
        
        # Search with automatic summarization
        query = "How to create REST APIs"
        result = doc_service.search_with_summary(query, k=3)
        
        print(f"Query: {result['query']}")
        print(f"Found {result['document_count']} documents")
        print(f"\nSummary:\n{result['summary']}")
        print("\nDocument sources:")
        for i, doc in enumerate(result['documents'], 1):
            source = doc['metadata'].get('source', 'Unknown')
            print(f"  {i}. {source}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure you have documents embedded in your vector store first")
    
    finally:
        # Service cleanup is automatic
        pass


def migration_example():
    """Example showing how to migrate from old summarize.py usage"""
    print("=== Migration from summarize.py ===")
    
    print("OLD WAY (summarize.py):")
    print("from summarize import summarize_search_results")
    print("summary = summarize_search_results(documents, query)")
    print()
    
    print("NEW WAY (SummaryService):")
    print("from core.services import SummaryService")
    print("summary_service = SummaryService(settings)")
    print("summary = summary_service.summarize_search_results(documents, query)")
    print()
    
    print("INTEGRATED WAY (DocumentService):")
    print("from core.services import DocumentService")
    print("doc_service = DocumentService(settings)")
    print("result = doc_service.search_with_summary(query)")
    print("summary = result['summary']")
    print()


if __name__ == "__main__":
    print("Summary Service Examples")
    print("=" * 50)
    
    # Show migration path
    migration_example()
    
    # Example 1: Independent SummaryService usage
    try:
        example_summary_service_usage()
    except Exception as e:
        print(f"SummaryService example failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your environment")
    
    # Example 2: Integrated DocumentService usage
    try:
        example_document_service_with_summary()
    except Exception as e:
        print(f"DocumentService example failed: {e}")
        print("This is expected if no documents are embedded yet")
    
    print("Examples completed!")
