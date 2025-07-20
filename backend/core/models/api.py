#!/usr/bin/env python3
"""
API request and response models for Doc2Dev backend
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class RepositoryRequest(BaseModel):
    """Request model for repository URL"""
    repo_url: HttpUrl
    library_name: Optional[str] = None  # Optional parameter, auto-generated from URL if not provided
    client_id: Optional[str] = None  # Client ID for WebSocket connection


class DownloadResponse(BaseModel):
    """Response model for download status"""
    status: str
    message: str
    files_count: int = 0
    files: List[str] = []
    download_url: Optional[str] = None
    embedding_status: Optional[str] = None
    embedding_count: int = 0
    table_name: Optional[str] = None  # Table name for query page navigation
    query_url: Optional[str] = None  # Query page URL for frontend link generation
    repo_path: Optional[str] = None  # Repository path for frontend display

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
    results: List[dict] = []
    summary: Optional[str] = None
