#!/usr/bin/env python3
"""
API request and response models for Doc2Dev backend
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from .repository import RepositorySource


class RepositoryRequest(BaseModel):
    """Request model for repository URL"""
    repo_url: HttpUrl
    library_name: Optional[str] = None  # Optional parameter, auto-generated from URL if not provided
    client_id: Optional[str] = None  # Client ID for WebSocket connection
    source: Optional[RepositorySource] = None  # Git platform source, auto-detected if not provided
    platform: Optional[str] = None  # Force specific platform ('github' or 'gitlab') for ambiguous URLs


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


class PlatformConfigRequest(BaseModel):
    """Request model for platform configuration validation"""
    platform: str  # 'github' or 'gitlab'
    url: Optional[str] = None  # Custom URL for enterprise/self-hosted instances
    token: Optional[str] = None  # Platform token for validation


class PlatformConfigResponse(BaseModel):
    """Response model for platform configuration status"""
    platform: str
    configured: bool
    valid: bool
    base_url: str
    api_url: str
    issues: List[str] = []
    warnings: List[str] = []


class PlatformStatusResponse(BaseModel):
    """Response model for all platforms status"""
    platforms: dict  # platform_name -> PlatformConfigResponse
    summary: dict  # Overall configuration summary


class UrlValidationRequest(BaseModel):
    """Request model for URL validation"""
    url: HttpUrl


class UrlValidationResponse(BaseModel):
    """Response model for URL validation"""
    valid: bool
    platform: Optional[str] = None
    org: Optional[str] = None
    repo: Optional[str] = None
    normalized_url: Optional[str] = None
    issues: List[str] = []
