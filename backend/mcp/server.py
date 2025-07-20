#!/usr/bin/env python3
"""
FastMCP server that provides a tool for fetching library documentation.
This server integrates with the Doc2Dev service layer architecture.
"""

import httpx
from typing import Dict, Any
from fastmcp import FastMCP

from config.settings import Settings
from core.services.repository import RepositoryService

# Initialize settings and services
settings = Settings()
repository_service = RepositoryService(settings)

# Get API base URL from settings
BASE_URL = settings.api_base_url

# Initialize FastMCP server
mcp = FastMCP()

@mcp.tool("search-library-id")
async def search_library_id(libraryName: str) -> Dict[str, Any]:
    """
    Resolves a general package name into a library ID by searching the repositories table.
    
    Args:
        libraryName: Library name to search for (e.g., "elasticsearch", "langchain")
        
    Returns:
        Dictionary containing matching library IDs and their descriptions
    """
    try:
        # Use RepositoryService to search repositories
        repositories = repository_service.search_repositories(libraryName)
        
        # Format the results
        libraries = []
        for repo in repositories:
            # Create libraryID by replacing slash with underscore in repository path
            # First remove the leading slash, then replace remaining slashes with underscores
            libraryID = repo.repo.lstrip('/').replace('/', '_')
            libraries.append({
                "libraryID": libraryID,
                "repository": repo.repo,
                "description": f"Table: {repo.name}, Repository: {repo.repo}",
                "status": repo.repo_status,
                "tokens": repo.tokens,
                "snippets": repo.snippets
            })
        
        return {
            "status": "success",
            "message": f"Found {len(libraries)} libraries matching '{libraryName}'",
            "libraries": libraries
        }
    
    except Exception as e:
        import traceback
        return {
            "error": "Failed to search for library ID",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@mcp.tool("get-library-docs")
async def get_library_docs(libraryID: str, question: str) -> Dict[str, Any]:
    """
    Fetches up-to-date documentation for a library.
    
    Args:
        libraryID: Table name in the vector database (e.g., 'kubernetes_sigs_kubebuilder')
        question: Question to ask about the library (e.g. How to use kubebuilder to write a Kubernetes Operator)
        
    Returns:
        Dictionary containing the documentation content
    """
    try:
        # Call the query API to get documentation using httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/query/",
                json={
                    "table_name": libraryID,
                    "query": question,
                    "k": 5,
                    "summarize": True  # Use summarization for better results
                },
                timeout=30.0  # Set a timeout for the request
            )
        
        if response.status_code != 200:
            return {
                "error": f"API request failed with status code {response.status_code}",
                "message": response.text
            }
        
        data = response.json()
        
        # Return documentation content
        return {
            "status": "success",
            "message": f"Retrieved documentation from table '{libraryID}'",
            "documentation": data.get("summary") or "No summary available",
            "results": data.get("results", [])
        }
    
    except Exception as e:
        import traceback
        return {
            "error": "Failed to get library documentation",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

def main():
    """Run the MCP server"""
    print("🚀 Starting Doc2Dev MCP Server...")
    print("📋 Available tools:")
    print("  - search-library-id: Search for library IDs by name")
    print("  - get-library-docs: Get documentation for a specific library")
    mcp.run()

if __name__ == "__main__":
    main()
