#!/usr/bin/env python3
"""
WebSocket routes for Doc2Dev API
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.websocket import manager

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time progress updates
    
    Args:
        websocket: WebSocket connection
        client_id: Client identifier for connection management
    """
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection active, wait for messages
            data = await websocket.receive_text()
            # Can process messages received from client, but here we mainly keep the connection
    except WebSocketDisconnect:
        manager.disconnect(client_id)
