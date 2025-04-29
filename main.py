#!/usr/bin/env python3
"""
FastAPI server that receives GitHub repository URLs and downloads markdown files.
"""

import os
from typing import List, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from github import Github, Auth, GithubException

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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class RepositoryRequest(BaseModel):
    """Request model for repository URL"""
    repo_url: HttpUrl

class DownloadResponse(BaseModel):
    """Response model for download status"""
    status: str
    message: str
    files_count: int = 0
    files: List[str] = []
    download_url: Optional[str] = None

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that serves the HTML interface"""
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return html_content

@app.get("/api/info")
async def api_info():
    """API info endpoint that returns basic information about the API"""
    return {"message": "GitHub Markdown Downloader API", "version": "1.0.0"}

@app.post("/download/", response_model=DownloadResponse)
async def download_repository(repo_request: RepositoryRequest):
    """
    Download markdown files from a GitHub repository directly to the project directory.

    Args:
        repo_request: Repository request containing URL

    Returns:
        JSON response with download status
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

        return DownloadResponse(
            status="success",
            message=f"Downloaded {files_count} markdown files to {output_dir}",
            files_count=files_count,
            files=files_list,
            download_url=None  # No download URL needed as files are saved directly
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Endpoint for downloading ZIP files removed - files are now saved directly to the project directory

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
