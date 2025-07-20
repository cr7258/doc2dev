#!/usr/bin/env python3
"""
WebSocket connection management utilities
"""

from typing import Dict, Any
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket connection manager for handling multiple client connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection and add it to active connections"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        """Remove a client connection from active connections"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_json(self, data: Dict[str, Any], client_id: str):
        """Send JSON data to a specific client"""
        try:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(data)
            else:
                print(f"Warning: Client {client_id} not found in active connections")
        except Exception as e:
            print(f"Error sending message to client {client_id}: {str(e)}")
            # If sending fails, try to remove the connection
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                print(f"Removed client {client_id} due to send error. Total connections: {len(self.active_connections)}")
            return False
        return True

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast JSON data to all active connections"""
        for connection in self.active_connections.values():
            await connection.send_json(data)



