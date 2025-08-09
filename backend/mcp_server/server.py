#!/usr/bin/env python3
"""
User-specific MCP server implementation for Doc2Dev.
Provides isolated MCP services for each user with access to their repositories.
"""

import logging
from typing import Dict, Any, List
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class UserMCPServer:
    """User-specific MCP server that provides access to user's repositories"""

    def __init__(self, user_id: str = None):
        self.user_id = user_id
        server_name = "Doc2Dev Public Server" if user_id is None else "Doc2Dev User Server"
        self.mcp = FastMCP(server_name)
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
                logger.info(f"Found {len(repositories)} total repositories for search")

                # Log first few repositories for debugging
                if repositories:
                    for i, repo in enumerate(repositories[:3]):
                        logger.info(f"Repo {i}: name='{repo.get('name', '')}', repo='{repo.get('repo', '')}', status='{repo.get('repo_status', '')}'")

                # Filter repositories based on library name (search both name and repo fields)
                # Only include completed repositories
                filtered_repos = [
                    repo for repo in repositories
                    if (libraryName.lower() in repo.get("name", "").lower() or
                        libraryName.lower() in repo.get("repo", "").lower()) and
                       repo.get("repo_status") == "completed"
                ]

                logger.info(f"Filtered to {len(filtered_repos)} repositories matching '{libraryName}'")
                
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
                
                access_type = "public access" if self.user_id is None else f"user {self.user_id}"
                return {
                    "status": "success",
                    "message": f"Found {len(libraries)} libraries matching '{libraryName}' for {access_type}",
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

        For authenticated users: Returns user-specific repositories from their private database.
        For public access (user_id=None): Returns public repositories.

        Returns:
            List of repository dictionaries for this user or public repositories
        """
        try:
            # Import here to avoid circular imports
            from main import repository_service

            if self.user_id is None:
                # Public access: get public repositories
                repositories = repository_service.get_all_repositories()
                access_type = "public"
            else:
                # User-specific access: get user's private repositories
                repositories = repository_service.get_user_repositories(self.user_id)
                access_type = f"user {self.user_id}"

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

            logger.info(f"Retrieved {len(repo_list)} repositories for {access_type}")
            return repo_list

        except Exception as e:
            logger.error(f"Error getting repositories for {self.user_id or 'public'}: {e}")
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
            from main import document_service

            # Call the document service directly with user_id to search user's repositories
            result = document_service.search_with_summary(
                query=question,
                table_name=library_id,
                k=5,
                filter=None,
                user_id=self.user_id
            )

            # Format results to match expected response structure
            formatted_results = []
            for i, doc_data in enumerate(result.get("documents", [])):
                formatted_results.append({
                    "id": str(i + 1),
                    "source": doc_data.get("metadata", {}).get("source", "Unknown"),
                    "content": doc_data.get("content", "")
                })

            access_type = "public access" if self.user_id is None else f"user {self.user_id}"
            return {
                "status": "success",
                "message": f"Retrieved documentation from table '{library_id}' for {access_type}",
                "documentation": result.get("summary", "No summary available"),
                "results": formatted_results
            }
                    
        except Exception as e:
            logger.error(f"Error querying library {library_id} for user {self.user_id}: {e}")
            return {
                "error": "Failed to query library",
                "message": str(e)
            }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information for this MCP server"""
        if self.user_id is None:
            server_name = "Doc2Dev Public MCP Server"
            description = "Public access to Doc2Dev documentation repositories"
        else:
            server_name = f"Doc2Dev MCP Server for {self.user_id}"
            description = f"User-specific access to Doc2Dev repositories for {self.user_id}"

        return {
            "name": server_name,
            "description": description,
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

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with the given arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Result from the tool execution
        """
        if tool_name not in self.tools:
            return {
                "error": "Tool not found",
                "message": f"Tool '{tool_name}' is not available"
            }

        try:
            tool_function = self.tools[tool_name]
            result = await tool_function(**arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "error": "Tool execution failed",
                "message": str(e)
            }
