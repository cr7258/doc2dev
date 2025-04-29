#!/usr/bin/env python3
"""
FastAPI server that receives GitHub repository URLs and downloads markdown files.
"""

import os
import sys
from typing import List, Optional, Dict
from urllib.parse import urlparse
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from github import Github, Auth, GithubException
from embed_and_store import load_markdown_files, split_documents, embed_and_store
from query_oceanbase import search_documents, connect_to_vector_store

# Load environment variables from .env file
load_dotenv()

# Get GitHub token from environment variables
DEFAULT_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
print(f"Loaded GitHub token from .env: {'*' * (len(DEFAULT_GITHUB_TOKEN) - 4) + DEFAULT_GITHUB_TOKEN[-4:] if DEFAULT_GITHUB_TOKEN else 'No token found'}")

app = FastAPI(
    title="GitHub Markdown Downloader",
    description="A service that downloads markdown files from GitHub repositories",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 前后端分离架构，不再需要挂载静态文件目录

class RepositoryRequest(BaseModel):
    """Request model for repository URL"""
    repo_url: HttpUrl
    library_name: Optional[str] = None  # 可选参数，如果前端没有提供，则自动从 URL 生成

class DownloadResponse(BaseModel):
    """Response model for download status"""
    status: str
    message: str
    files_count: int = 0
    files: List[str] = []
    download_url: Optional[str] = None
    embedding_status: Optional[str] = None
    embedding_count: int = 0

# No need to store temporary directories anymore - files are saved directly to the project directory

def parse_github_url(url: str) -> str:
    """
    Parse a GitHub URL to extract the repository name in the format 'owner/repo'.

    Args:
        url: GitHub repository URL

    Returns:
        Repository name in the format 'owner/repo'
    """
    parsed_url = urlparse(url)

    # Ensure it's a GitHub URL
    if not parsed_url.netloc.endswith('github.com'):
        raise ValueError("Not a valid GitHub URL")

    # Extract path parts
    path_parts = parsed_url.path.strip('/').split('/')

    # Ensure we have at least owner and repo
    if len(path_parts) < 2:
        raise ValueError("URL does not contain a valid repository path")

    # Return owner/repo format
    return f"{path_parts[0]}/{path_parts[1]}"

def get_contents_recursively(repo, path):
    """
    Recursively get all contents of a repository.

    Args:
        repo: GitHub repository object
        path: Path to get contents from

    Returns:
        list: List of content objects
    """
    contents = []

    try:
        items = repo.get_contents(path)

        for item in items:
            if item.type == "dir":
                # Recursively get contents of directories
                contents.extend(get_contents_recursively(repo, item.path))
            else:
                contents.append(item)
    except Exception as e:
        print(f"Error accessing {path}: {e}")

    return contents

def download_md_files(repo_name, output_dir=None, token=None):
    """
    Download all markdown files from a GitHub repository.

    Args:
        repo_name (str): The repository name in the format 'owner/repo'
        output_dir (str, optional): Directory to save downloaded files. Defaults to a directory named after the repo.
        token (str, optional): GitHub personal access token for authentication. Public repos don't require this.

    Returns:
        tuple: (success, message, files_count, files_list)
    """
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = repo_name.split('/')[-1] + '_md_files'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    downloaded_files = []

    try:
        # Initialize GitHub client
        if token and isinstance(token, str) and token.strip():
            # Use provided token if available and not empty
            masked_token = '*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'
            print(f"Using provided token: {masked_token}")
            auth = Auth.Token(token.strip())
            g = Github(auth=auth)
        elif DEFAULT_GITHUB_TOKEN and DEFAULT_GITHUB_TOKEN.strip():
            # Fall back to token from .env file
            masked_token = '*' * (len(DEFAULT_GITHUB_TOKEN) - 4) + DEFAULT_GITHUB_TOKEN[-4:] if len(DEFAULT_GITHUB_TOKEN) > 4 else '****'
            print(f"Using GitHub token from .env file: {masked_token}")
            auth = Auth.Token(DEFAULT_GITHUB_TOKEN.strip())
            g = Github(auth=auth)
        else:
            # No token available, use unauthenticated client (rate limited)
            print("Warning: No GitHub token provided. API requests may be rate limited.")
            g = Github()

        # Print rate limit info
        try:
            rate_limit = g.get_rate_limit()
            print(f"GitHub API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit} requests remaining")
        except Exception as e:
            print(f"Could not get rate limit info: {str(e)}")

        # Get the repository
        repo = g.get_repo(repo_name)
        print(f"Repository: {repo.full_name}")

        # Get all contents recursively
        contents = get_contents_recursively(repo, "")

        # Filter and download markdown files
        md_files_count = 0
        for content in contents:
            if content.path.endswith('.md'):
                # Create subdirectories if needed
                file_path = os.path.join(output_dir, content.path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Get file content
                file_content = repo.get_contents(content.path).decoded_content

                # Write to file
                with open(file_path, 'wb') as f:
                    f.write(file_content)

                downloaded_files.append(content.path)
                md_files_count += 1

        # Close the connection
        g.close()

        return True, f"Downloaded {md_files_count} markdown files", md_files_count, downloaded_files

    except GithubException as e:
        error_message = f"GitHub API error: {e.status} - {e.data.get('message', str(e))}"
        print(f"GitHub Exception: {error_message}")
        print(f"Exception details: {e}")
        return False, error_message, 0, []
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(f"General Exception: {error_message}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False, error_message, 0, []

# ZIP archive creation function removed - files are saved directly to the project directory

@app.get("/")
async def root():
    """API 根端点，返回基本信息"""
    return {
        "status": "success",
        "message": "Doc2Dev API is running",
        "version": "1.0.0",
        "endpoints": [
            "/api/info",
            "/download/",
            "/query/"
        ]
    }

@app.get("/api/info")
async def api_info():
    """API info endpoint that returns basic information about the API"""
    return {"message": "GitHub Markdown Downloader API", "version": "1.0.0"}

@app.post("/download/", response_model=DownloadResponse)
async def download_repository(repo_request: RepositoryRequest):
    """
    Download markdown files from a GitHub repository directly to the project directory
    and automatically embed them if embedding functionality is available.

    Args:
        repo_request: Repository request containing URL

    Returns:
        JSON response with download status and embedding status
    """
    try:
        # Parse GitHub URL to get repo name
        repo_name = parse_github_url(str(repo_request.repo_url))

        # Get repository name for the output directory
        repo_dir_name = repo_name.split('/')[-1]

        # Create output directory in the project root
        output_dir = os.path.join(os.getcwd(), f"{repo_dir_name}_md_files")

        # Download markdown files - always use token from .env file
        success, message, files_count, files_list = download_md_files(
            repo_name,
            output_dir=output_dir,
            token=None  # Always use token from .env file
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        # Initialize embedding status variables
        embedding_status = "skipped"
        embedding_count = 0

        # Automatically embed documents if embedding functionality is available
        if files_count > 0:
            try:
                print(f"Starting automatic embedding of {files_count} markdown files...")

                # Load documents
                documents = load_markdown_files(output_dir)

                if documents:
                    # Split documents
                    split_docs = split_documents(documents)

                    # Embed and store documents
                    if repo_request.library_name:
                        # 如果前端提供了 library_name，则直接使用，但确保将连字符替换为下划线
                        table_name = repo_request.library_name.replace('-', '_')
                    else:
                        # 否则从 GitHub URL 中提取用户名和仓库名
                        # 例如：https://github.com/cr7258/elasticsearch-mcp-server -> cr7258_elasticsearch_mcp_server
                        repo_parts = repo_name.split('/')
                        if len(repo_parts) == 2:
                            owner, repo = repo_parts
                            # 替换连字符为下划线以避免 SQL 语法错误
                            safe_owner = owner.replace('-', '_')
                            safe_repo = repo.replace('-', '_')
                            table_name = f"{safe_owner}_{safe_repo}"
                        else:
                            # 如果无法正确解析，则使用原来的方式
                            safe_repo_name = repo_dir_name.replace('-', '_')
                            table_name = f"{safe_repo_name}_vectors"
                    vector_store = embed_and_store(
                        split_docs,
                        table_name=table_name,
                        drop_old=True
                    )

                    embedding_status = "success"
                    embedding_count = len(split_docs)
                    print(f"Successfully embedded {embedding_count} document chunks into table '{table_name}'")
                else:
                    embedding_status = "no_documents"
                    print("No documents were loaded for embedding")
            except Exception as e:
                embedding_status = f"error: {str(e)}"
                print(f"Error during embedding: {str(e)}")
                import traceback
                print(f"Embedding traceback: {traceback.format_exc()}")

        return DownloadResponse(
            status="success",
            message=f"Downloaded {files_count} markdown files to {output_dir}",
            files_count=files_count,
            files=files_list,
            download_url=None,  # No download URL needed as files are saved directly
            embedding_status=embedding_status,
            embedding_count=embedding_count
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Endpoint for downloading ZIP files removed - files are now saved directly to the project directory

class QueryRequest(BaseModel):
    """Request model for vector database query"""
    query: str
    table_name: str
    k: int = 5
    summarize: bool = False

class QueryResponse(BaseModel):
    """Response model for vector database query"""
    status: str
    message: str
    results: List[Dict[str, str]] = []
    summary: Optional[str] = None

@app.post("/query/", response_model=QueryResponse)
async def query_vector_database(query_request: QueryRequest):
    """
    Query the vector database for documents similar to the query.

    Args:
        query_request: Query request containing query string and table name

    Returns:
        JSON response with query results
    """
    try:
        # Search for documents with optional summarization
        results, summary = search_documents(
            query=query_request.query,
            k=query_request.k,
            table_name=query_request.table_name,
            summarize=query_request.summarize
        )

        # Format results
        formatted_results = []
        for i, doc in enumerate(results):
            formatted_results.append({
                "id": str(i + 1),
                "source": doc.metadata.get("source", "Unknown"),
                "content": doc.page_content
            })

        return QueryResponse(
            status="success",
            message=f"Found {len(results)} results for query: '{query_request.query}'",
            results=formatted_results,
            summary=summary
        )

    except Exception as e:
        return QueryResponse(
            status="error",
            message=f"Error querying vector database: {str(e)}"
        )

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
