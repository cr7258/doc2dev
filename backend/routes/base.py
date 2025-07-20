#!/usr/bin/env python3
"""
Base routes for Doc2Dev API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """API root endpoint, returns basic information"""
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


@router.get("/api/info")
async def api_info():
    """API info endpoint that returns basic information about the API"""
    return {"message": "GitHub Markdown Downloader API", "version": "1.0.0"}
