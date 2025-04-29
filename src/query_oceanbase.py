#!/usr/bin/env python3
"""
Script to query vectors stored in OceanBase.
"""

import os
import argparse
from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_oceanbase.vectorstores import OceanbaseVectorStore
from summarize import summarize_search_results

# Load environment variables
load_dotenv()

# Get API key from environment
DASHSCOPE_API = os.environ.get("DASHSCOPE_API_KEY", "")
if not DASHSCOPE_API:
    raise ValueError("DASHSCOPE_API_KEY environment variable is not set")

# Default OceanBase connection arguments
DEFAULT_CONNECTION_ARGS = {
    "host": "127.0.0.1",
    "port": "2881",
    "user": "root@test",
    "password": "admin",
    "db_name": "doc2dev",
}

def connect_to_vector_store(
    connection_args=DEFAULT_CONNECTION_ARGS,
    table_name="langchain_vector"
):
    """
    Connect to the OceanBase vector store.
    
    Args:
        connection_args: OceanBase connection arguments
        table_name: Name of the table containing vectors
        
    Returns:
        OceanbaseVectorStore object
    """
    # Initialize the embedding model
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v3", dashscope_api_key=DASHSCOPE_API
    )
    
    # Sanitize table name by replacing hyphens with underscores to avoid SQL syntax errors
    safe_table_name = table_name.replace('-', '_')
    
    # Connect to the vector store
    vector_store = OceanbaseVectorStore(
        embedding_function=embeddings,
        table_name=safe_table_name,
        connection_args=connection_args,
    )
    
    return vector_store

def search_documents(query, k=5, filter=None, table_name="langchain_vector", summarize=False):
    """
    Search for documents similar to the query.
    
    Args:
        query: Query string
        k: Number of results to return
        filter: Filter to apply to the search
        table_name: Name of the table containing vectors
        summarize: Whether to summarize the search results using OpenAI API
        
    Returns:
        tuple: (List of Document objects, summary string if summarize=True else None)
    """
    print(f"Connecting to OceanBase vector store (table: {table_name})...")
    vector_store = connect_to_vector_store(table_name=table_name)
    
    print(f"Searching for documents similar to: '{query}'")
    results = vector_store.similarity_search(
        query=query,
        k=k,
        filter=filter
    )
    
    print(f"Found {len(results)} results")
    
    # Generate summary if requested
    summary = None
    if summarize and results:
        print("Generating summary using OpenAI API...")
        summary = summarize_search_results(results, query)
    
    return results, summary

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Query vectors stored in OceanBase")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--table-name", default="langchain_vector", help="Name of the table containing vectors")
    parser.add_argument("--filter-source", help="Filter results by source")
    
    args = parser.parse_args()
    
    # Create filter if source is provided
    filter = {"source": args.filter_source} if args.filter_source else None
    
    # Add argument for summarization
    parser.add_argument("--summarize", action="store_true", help="Summarize results using OpenAI API")
    
    args = parser.parse_args()
    
    # Create filter if source is provided
    filter = {"source": args.filter_source} if args.filter_source else None
    
    # Search for documents
    results, summary = search_documents(
        args.query,
        k=args.k,
        filter=filter,
        table_name=args.table_name,
        summarize=args.summarize
    )
    
    # Print results
    print("\nSearch Results:")
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content: {doc.page_content}")
        print("-" * 50)
    
    # Print summary if available
    if summary:
        print("\nSummary:")
        print(summary)

if __name__ == "__main__":
    main()
