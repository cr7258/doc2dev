#!/usr/bin/env python3
"""
MCP Streamable HTTP routes for Doc2Dev API.
Provides user-specific MCP endpoints following the MCP Streamable HTTP protocol.
"""

import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from mcp_server.server import UserMCPServer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP Streamable HTTP"])

# Cache for user MCP server instances
user_servers: Dict[str, UserMCPServer] = {}


def get_user_server(user_id: str) -> UserMCPServer:
    """Get or create user MCP server instance"""
    if user_id not in user_servers:
        logger.info(f"Creating new MCP server instance for user {user_id}")
        user_servers[user_id] = UserMCPServer(user_id)
    return user_servers[user_id]


@router.get("/health")
async def mcp_health():
    """
    Health check endpoint for MCP service.

    Returns:
        Health status of the MCP service
    """
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "service": "MCP Streamable HTTP",
        "active_servers": len(user_servers),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.api_route("/{user_id}", methods=["GET", "POST"])
async def mcp_streamable_endpoint(user_id: str, request: Request):
    """
    MCP Streamable HTTP endpoint for a specific user.
    
    - GET: Returns server information and capabilities
    - POST: Processes MCP protocol messages
    
    Args:
        user_id: Unique identifier for the user
        request: FastAPI request object
        
    Returns:
        JSON response following MCP protocol
    """
    try:
        server = get_user_server(user_id)
        
        if request.method == "GET":
            # Return MCP server information
            logger.info(f"GET request for user {user_id} MCP server info")
            return JSONResponse(content=server.get_server_info())
        
        elif request.method == "POST":
            # Process MCP protocol message
            try:
                body = await request.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON body: {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON in request body")
            
            logger.info(f"POST request for user {user_id}: {body.get('method', 'unknown')}")
            
            # Validate MCP message structure
            if "method" not in body:
                raise HTTPException(status_code=400, detail="Missing 'method' field in MCP message")
            
            method = body["method"]
            params = body.get("params", {})
            message_id = body.get("id")
            
            # Handle different MCP methods
            if method == "initialize":
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {
                            "tools": {"listChanged": False}
                        },
                        "serverInfo": {
                            "name": "Doc2Dev",
                            "version": "1.0.0"
                        }
                    }
                })
            
            elif method == "tools/list":
                tools = server.get_tools_list()
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {"tools": tools}
                })
            
            elif method == "notifications/initialized":
                # Handle the initialized notification
                # This is sent by the client after successful initialization
                # We don't need to return anything for notifications
                logger.info(f"Client initialized notification received for user {user_id}")
                return JSONResponse(content={})

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if not tool_name:
                    raise HTTPException(status_code=400, detail="Missing tool name in tools/call")

                # Call the appropriate tool
                if tool_name == "search-library-id":
                    library_name = arguments.get("libraryName", "")
                    if not library_name:
                        raise HTTPException(status_code=400, detail="Missing libraryName argument")

                    # Get the tool function from the server
                    tool_func = server.tools.get("search-library-id")
                    if not tool_func:
                        raise HTTPException(status_code=500, detail="Tool not found")

                    result = await tool_func(library_name)

                elif tool_name == "get-library-docs":
                    library_id = arguments.get("libraryID", "")
                    question = arguments.get("question", "")

                    if not library_id or not question:
                        raise HTTPException(
                            status_code=400,
                            detail="Missing libraryID or question argument"
                        )

                    # Get the tool function from the server
                    tool_func = server.tools.get("get-library-docs")
                    if not tool_func:
                        raise HTTPException(status_code=500, detail="Tool not found")

                    result = await tool_func(library_id, question)

                else:
                    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

                # Format the response according to MCP protocol
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, ensure_ascii=False)
                            }
                        ]
                    }
                })

            else:
                raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in MCP endpoint for user {user_id}: {e}")
        
        # Return MCP error response
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if 'body' in locals() else None,
                "error": {
                    "code": -32000,
                    "message": f"Internal server error: {str(e)}"
                }
            }
        )


@router.get("/")
async def mcp_info():
    """
    General MCP service information endpoint.
    
    Returns:
        Information about the MCP service
    """
    return {
        "service": "Doc2Dev MCP Streamable HTTP",
        "version": "1.0.0",
        "protocol_version": "2025-03-26",
        "description": "User-specific MCP endpoints for accessing Doc2Dev documentation",
        "usage": {
            "endpoint_pattern": "/mcp/{user_id}",
            "methods": ["GET", "POST"],
            "get_description": "Returns server information and capabilities",
            "post_description": "Processes MCP protocol messages"
        },
        "available_tools": [
            "search-library-id",
            "get-library-docs"
        ]
    }



