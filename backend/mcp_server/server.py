#!/usr/bin/env python3
"""
User-specific MCP server implementation for Doc2Dev.
Provides isolated MCP services for each user with access to their repositories.
"""

import logging
import httpx
from typing import Dict, Any, List
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class UserMCPServer:
    """User-specific MCP server that provides access to user's repositories"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.mcp = FastMCP("Doc2Dev User Server")
        self.tools = {}
        self.setup_tools()

    def setup_tools(self):
        """Setup MCP tools for this user"""

        async def search_library_id(libraryName: str) -> Dict[str, Any]:
            """
            Search for library IDs by name within user's accessible repositories.
            
            Args:
                libraryName: Name of the library to search for
                
            Returns:
                Dictionary containing matching library IDs and their descriptions
            """
            try:
                repositories = await self.get_user_repositories()
                
                # Filter repositories based on library name
                filtered_repos = [
                    repo for repo in repositories 
                    if libraryName.lower() in repo.get("name", "").lower()
                ]
                
                # Format the results
                libraries = []
                for repo in filtered_repos:
                    # Create libraryID by replacing slash with underscore in repository path
                    repo_path = repo.get("repo", "")
                    libraryID = repo_path.lstrip('/').replace('/', '_')
                    
                    libraries.append({
                        "libraryID": libraryID,
                        "repository": repo_path,
                        "description": f"Table: {repo.get('name', '')}, Repository: {repo_path}",
                        "status": repo.get("repo_status", "unknown"),
                        "tokens": repo.get("tokens", 0),
                        "snippets": repo.get("snippets", 0)
                    })
                
                return {
                    "status": "success",
                    "message": f"Found {len(libraries)} libraries matching '{libraryName}' for user {self.user_id}",
                    "libraries": libraries
                }

            except Exception as e:
                logger.error(f"Error searching library ID for user {self.user_id}: {e}")
                return {
                    "error": "Failed to search for library ID",
                    "message": str(e)
                }

        async def get_library_docs(libraryID: str, question: str) -> Dict[str, Any]:
            """
            Get documentation for a specific library accessible to the user.
            
            Args:
                libraryID: Table name in the vector database (e.g., 'kubernetes_sigs_kubebuilder')
                question: Question to ask about the library
                
            Returns:
                Dictionary containing the documentation content
            """
            try:
                return await self.query_user_library(libraryID, question)
                
            except Exception as e:
                logger.error(f"Error getting library docs for user {self.user_id}: {e}")
                return {
                    "error": "Failed to get library documentation",
                    "message": str(e)
                }

        # Store the tool functions
        self.tools["search-library-id"] = search_library_id
        self.tools["get-library-docs"] = get_library_docs
    
    async def get_user_repositories(self) -> List[Dict[str, Any]]:
        """
        Get repositories accessible to this user.
        
        For now, this returns all repositories. In the future, this can be enhanced
        to filter based on user permissions, ownership, or access rights.
        
        Returns:
            List of repository dictionaries
        """
        try:
            # Import here to avoid circular imports
            from main import repository_service
            
            # Get all repositories (future: filter by user access)
            repositories = repository_service.get_all_repositories()
            
            # Convert to dictionary format
            repo_list = []
            for repo in repositories:
                repo_list.append({
                    "id": repo.id,
                    "name": repo.name,
                    "description": repo.description,
                    "repo": repo.repo,
                    "repo_url": repo.repo_url,
                    "repo_status": repo.repo_status,
                    "tokens": repo.tokens,
                    "snippets": repo.snippets,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                })
            
            logger.info(f"Retrieved {len(repo_list)} repositories for user {self.user_id}")
            return repo_list
            
        except Exception as e:
            logger.error(f"Error getting user repositories for user {self.user_id}: {e}")
            return []
    
    async def query_user_library(self, library_id: str, question: str) -> Dict[str, Any]:
        """
        Query a specific library's documentation for the user.
        
        Args:
            library_id: The library ID (table name)
            question: The question to ask about the library
            
        Returns:
            Dictionary containing query results
        """
        try:
            # Import here to avoid circular imports
            from main import settings
            
            # Call the query API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.api_base_url}/query/",
                    json={
                        "table_name": library_id,
                        "query": question,
                        "k": 5,
                        "summarize": True
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "success",
                        "message": f"Retrieved documentation from table '{library_id}' for user {self.user_id}",
                        "documentation": data.get("summary", "No summary available"),
                        "results": data.get("results", [])
                    }
                else:
                    return {
                        "error": f"API request failed with status code {response.status_code}",
                        "message": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error querying library {library_id} for user {self.user_id}: {e}")
            return {
                "error": "Failed to query library",
                "message": str(e)
            }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information for this user's MCP server"""
        return {
            "name": f"Doc2Dev MCP Server for {self.user_id}",
            "version": "1.0.0",
            "protocol_version": "2025-03-26",
            "transport": "streamable-http",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False
            }
        }
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools for this user"""
        return [
            {
                "name": "search-library-id",
                "description": "Search for library IDs by name within user's accessible repositories",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "libraryName": {
                            "type": "string",
                            "description": "Name of the library to search for"
                        }
                    },
                    "required": ["libraryName"]
                }
            },
            {
                "name": "get-library-docs",
                "description": "Get documentation for a specific library accessible to the user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "libraryID": {
                            "type": "string",
                            "description": "Table name in the vector database (e.g., 'kubernetes_sigs_kubebuilder')"
                        },
                        "question": {
                            "type": "string",
                            "description": "Question to ask about the library"
                        }
                    },
                    "required": ["libraryID", "question"]
                }
            }
        ]
