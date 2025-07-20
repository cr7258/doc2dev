#!/usr/bin/env python3
"""
Routes package for Doc2Dev API
"""

from .base import router as base_router
from .repository import router as repository_router
from .query import router as query_router
from .websocket import router as websocket_router

__all__ = [
    "base_router",
    "repository_router", 
    "query_router",
    "websocket_router"
]