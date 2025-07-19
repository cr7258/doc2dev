#!/usr/bin/env python3
"""
Document Service Example

This example demonstrates how to use the DocumentService for complete document processing.
"""

import os
from dotenv import load_dotenv
from config.settings import Settings
from core.services.document import DocumentService

# Load environment variables
load_dotenv()

def main():
    """
    Example usage of DocumentService for document processing.
    """
    
    print("=== Document Service Example ===")
    
    # Load configuration
    settings = Settings()
    
    print(f"Configuration loaded:")
    print(f"  Vector Store: {settings.vector_store.config.type}")
    print(f"  Embedding: {settings.embedding.config.type}")
    print(f"  Metadata DB: {settings.metadata_db.config.type}")
    print()
    
    # Create document service
    doc_service = DocumentService(settings)
    
    # Example 1: Process documents from directory
    print("=== Example 1: Process documents from directory ===")
    
    # You can specify a directory containing md, txt, pdf files
    # doc_service.process_documents("path/to/your/docs", drop_old=True)
    
    # Example 2: Process specific files
    print("=== Example 2: Process specific files ===")
    
    # Create some sample files for demonstration
    sample_files = create_sample_files()
    
    try:
        # Process the sample files
        success = doc_service.process_documents(sample_files, drop_old=False)
        
        if success:
            print("✅ Document processing completed successfully!")
            
            # Example 3: Search documents
            print("\n=== Example 3: Search documents ===")
            
            # Search for similar documents
            query = "What is Python?"
            results = doc_service.search_documents(query, k=3)
            
            print(f"Search results for '{query}':")
            for i, doc in enumerate(results, 1):
                print(f"  {i}. {doc.page_content[:100]}...")
                print(f"     Source: {doc.metadata.get('file_name', 'Unknown')}")
                print()
            
            # Example 4: Search with scores
            print("=== Example 4: Search with scores ===")
            
            scored_results = doc_service.search_with_scores(query, k=3)
            
            print(f"Search results with scores for '{query}':")
            for i, (doc, score) in enumerate(scored_results, 1):
                print(f"  {i}. Score: {score:.4f}")
                print(f"     Content: {doc.page_content[:80]}...")
                print(f"     Source: {doc.metadata.get('file_name', 'Unknown')}")
                print()
        
        else:
            print("❌ Document processing failed")
            
    finally:
        # Clean up sample files
        cleanup_sample_files(sample_files)

def create_sample_files():
    """Create sample files for demonstration"""
    
    sample_dir = "temp_samples"
    os.makedirs(sample_dir, exist_ok=True)
    
    files = []
    
    # Sample Markdown file
    md_content = """# Python Programming Guide

## Introduction
Python is a high-level programming language known for its simplicity and readability.

## Features
- Easy to learn and use
- Extensive standard library
- Cross-platform compatibility

### Code Example
```python
def hello_world():
    print("Hello, World!")
```

## Conclusion
Python is an excellent choice for beginners and experts alike.
"""
    
    md_file = os.path.join(sample_dir, "python_guide.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    files.append(md_file)
    
    # Sample text file
    txt_content = """Machine Learning Basics

Machine learning is a subset of artificial intelligence that focuses on algorithms 
that can learn and make decisions from data.

Key concepts include:
- Supervised learning
- Unsupervised learning
- Neural networks
- Deep learning

Applications of machine learning are found in many areas including:
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles
"""
    
    txt_file = os.path.join(sample_dir, "ml_basics.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    files.append(txt_file)
    
    print(f"Created sample files: {[os.path.basename(f) for f in files]}")
    return files

def cleanup_sample_files(files):
    """Clean up sample files"""
    import shutil
    
    for file in files:
        if os.path.exists(file):
            os.remove(file)
    
    # Remove sample directory if empty
    sample_dir = os.path.dirname(files[0]) if files else None
    if sample_dir and os.path.exists(sample_dir):
        try:
            os.rmdir(sample_dir)
            print(f"Cleaned up sample directory: {sample_dir}")
        except OSError:
            pass  # Directory not empty

if __name__ == "__main__":
    main()
