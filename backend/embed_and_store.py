#!/usr/bin/env python3
"""
Script to embed Markdown files and store them in OceanBase.
"""

import os
import glob
from typing import List, Dict, Optional
import argparse
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_oceanbase.vectorstores import OceanbaseVectorStore

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

def load_markdown_files(path_or_paths) -> List[Document]:
    """
    Load Markdown files from a directory, file path, or list of file paths.
    
    Args:
        path_or_paths: Directory containing Markdown files, a single file path, or a list of file paths
        
    Returns:
        List of Document objects
    """
    documents = []
    md_files = []
    
    # 处理不同类型的输入
    if isinstance(path_or_paths, list):
        # 如果输入是文件路径列表
        print(f"Loading {len(path_or_paths)} Markdown files from provided list...")
        md_files = path_or_paths
    elif os.path.isdir(path_or_paths):
        # 如果输入是目录
        directory = path_or_paths
        print(f"Loading Markdown files from directory: {directory}...")
        # 查找目录及其子目录中的所有 .md 文件
        md_files = glob.glob(f"{directory}/**/*.md", recursive=True)
        print(f"Found {len(md_files)} Markdown files in directory")
    elif os.path.isfile(path_or_paths) and path_or_paths.lower().endswith('.md'):
        # 如果输入是单个文件
        print(f"Loading single Markdown file: {path_or_paths}")
        md_files = [path_or_paths]
    else:
        print(f"Warning: Invalid input to load_markdown_files: {path_or_paths}")
        return []
    
    # 处理找到的所有文件
    for file_path in md_files:
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建源文件的路径
            # 如果是文件列表，使用文件名作为源
            # 如果是目录，创建相对路径
            if isinstance(path_or_paths, list) or os.path.isfile(path_or_paths):
                source_path = os.path.basename(file_path)
            else:
                # 假设是目录，创建相对路径
                directory = path_or_paths if os.path.isdir(path_or_paths) else os.path.dirname(path_or_paths)
                source_path = os.path.relpath(file_path, directory)
            
            # 创建 Document 对象
            doc = Document(
                page_content=content,
                metadata={
                    "source": source_path,
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_type": "markdown"
                }
            )
            documents.append(doc)
            print(f"Loaded: {source_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
    
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents based on Markdown headers to preserve document structure.
    
    Args:
        documents: List of Document objects
        
    Returns:
        List of split Document objects
    """
    print("Splitting documents based on Markdown headers...")
    
    # Define headers to split on
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
        ("#####", "Header 5"),
        ("######", "Header 6"),
    ]
    
    # Create a Markdown header text splitter
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    
    all_splits = []
    
    for doc in documents:
        try:
            # Split by headers
            header_splits = header_splitter.split_text(doc.page_content)
            
            # Add splits to the result list
            all_splits.extend(header_splits)
        except Exception as e:
            print(f"Error splitting document {doc.metadata.get('source', 'unknown')}: {str(e)}")
            # If header splitting fails, keep the document as is
            all_splits.append(doc)
    
    print(f"Split {len(documents)} documents into {len(all_splits)} chunks")
    return all_splits

def embed_and_store(
    documents: List[Document],
    connection_args: Dict[str, str] = DEFAULT_CONNECTION_ARGS,
    table_name: str = "langchain_vector",
    drop_old: bool = False
) -> OceanbaseVectorStore:
    """
    Embed documents and store them in OceanBase.
    
    Args:
        documents: List of Document objects
        connection_args: OceanBase connection arguments
        table_name: Name of the table to store vectors
        drop_old: Whether to drop the existing table
        
    Returns:
        OceanbaseVectorStore object
    """
    print(f"Embedding and storing {len(documents)} documents in OceanBase...")
    
    # Initialize the embedding model
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v3", dashscope_api_key=DASHSCOPE_API
    )
    
    # Create the vector store
    vector_store = OceanbaseVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        connection_args=connection_args,
        table_name=table_name,
        vidx_metric_type="l2",
        drop_old=drop_old
    )
    
    print(f"Successfully embedded and stored {len(documents)} documents in OceanBase")
    
    return vector_store

def search_documents(
    vector_store: OceanbaseVectorStore,
    query: str,
    k: int = 5,
    filter: Optional[Dict[str, str]] = None
) -> List[Document]:
    """
    Search for documents similar to the query.
    
    Args:
        vector_store: OceanbaseVectorStore object
        query: Query string
        k: Number of results to return
        filter: Filter to apply to the search
        
    Returns:
        List of Document objects
    """
    print(f"Searching for documents similar to: '{query}'")
    
    results = vector_store.similarity_search(
        query=query,
        k=k,
        filter=filter
    )
    
    print(f"Found {len(results)} results")
    
    return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Embed Markdown files and store them in OceanBase")
    parser.add_argument("directory", help="Directory containing Markdown files")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Maximum size of each chunk")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Overlap between chunks")
    parser.add_argument("--table-name", default="langchain_vector", help="Name of the table to store vectors")
    parser.add_argument("--drop-old", action="store_true", help="Drop the existing table")
    parser.add_argument("--search", help="Search query (optional)")
    parser.add_argument("--k", type=int, default=5, help="Number of search results to return")
    
    args = parser.parse_args()
    
    # Load documents
    documents = load_markdown_files(args.directory)
    
    if not documents:
        print("No documents found. Exiting.")
        return
    
    # Split documents
    split_docs = split_documents(documents, args.chunk_size, args.chunk_overlap)
    
    # Embed and store documents
    vector_store = embed_and_store(
        split_docs,
        table_name=args.table_name,
        drop_old=args.drop_old
    )
    
    # Search if a query is provided
    if args.search:
        results = search_documents(vector_store, args.search, args.k)
        
        print("\nSearch Results:")
        for i, doc in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content: {doc.page_content[:200]}...")

if __name__ == "__main__":
    main()
