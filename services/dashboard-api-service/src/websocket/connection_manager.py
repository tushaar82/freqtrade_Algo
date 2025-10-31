"""
WebSocket Connection Manager
VELOX Trading Platform
"""
import logging
from typing import Dict, List, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}
        self.subscriptions: Dict[UUID, Set[str]] = {}
        self.filters: Dict[UUID, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.subscriptions[user_id] = set()
        self.filters[user_id] = {}
        logger.info(f"WebSocket connected: {user_id}")
    
    async def disconnect(self, websocket: WebSocket, user_id: UUID):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.subscriptions:
            del self.subscriptions[user_id]
        if user_id in self.filters:
            del self.filters[user_id]
        logger.info(f"WebSocket disconnected: {user_id}")
    
    async def subscribe(self, user_id: UUID, streams: List[str], filters: dict):
        """Subscribe user to streams"""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].update(streams)
            self.filters[user_id] = filters
            logger.info(f"User {user_id} subscribed to: {streams}")
    
    async def unsubscribe(self, user_id: UUID, streams: List[str]):
        """Unsubscribe user from streams"""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].difference_update(streams)
            logger.info(f"User {user_id} unsubscribed from: {streams}")
    
    async def send_to_user(self, user_id: UUID, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            
            # Check if user is subscribed to this message type
            msg_type = message.get("type", "").lower()
            if msg_type in self.subscriptions.get(user_id, set()):
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
