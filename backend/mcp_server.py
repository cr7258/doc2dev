#!/usr/bin/env python3
"""
FastMCP server that provides a tool for fetching library documentation.
This server integrates with the existing vector database query API.
"""

import httpx
import pymysql
from typing import Dict, Any, Optional
from fastmcp import FastMCP

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Default OceanBase connection arguments
DB_CONNECTION_ARGS = {
    "host": "127.0.0.1",
    "port": 2881,
    "user": "root@test",
    "password": "admin",
    "database": "doc2dev",
    "charset": "utf8mb4"
}

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
        # Connect to the database
        connection = pymysql.connect(**DB_CONNECTION_ARGS)
        
        try:
            with connection.cursor() as cursor:
                # Execute the query with LIKE for fuzzy matching
                search_term = f"%{libraryName}%"
                query = "SELECT name, repo FROM repositories WHERE name LIKE %s OR repo LIKE %s"
                cursor.execute(query, (search_term, search_term))
                
                # Fetch all matching records
                results = cursor.fetchall()
                
                # Format the results
                libraries = []
                for name, repo in results:
                    # Create libraryID by replacing slash with underscore in repository path
                    # First remove the leading slash, then replace remaining slashes with underscores
                    libraryID = repo.lstrip('/').replace('/', '_')
                    libraries.append({
                        "libraryID": libraryID,
                        "repository": repo,
                        "description": f"Table: {name}, Repository: {repo}"
                    })
                
                return {
                    "status": "success",
                    "message": f"Found {len(libraries)} libraries matching '{libraryName}'",
                    "libraries": libraries
                }
        finally:
            connection.close()
    
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
    # Run the MCP server
    mcp.run()

if __name__ == "__main__":
    main()
