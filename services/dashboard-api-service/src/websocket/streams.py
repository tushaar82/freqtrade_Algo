"""
WebSocket Streams for Real-Time Dashboard
VELOX Trading Platform
"""
import json
import logging
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from .connection_manager import ConnectionManager
from .redis_pubsub import RedisPubSubManager

logger = logging.getLogger(__name__)


class DashboardStreams:
    """Manage WebSocket streams for dashboard"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.redis_pubsub = RedisPubSubManager()
    
    async def handle_connection(self, websocket: WebSocket, user_id: UUID):
        """Handle WebSocket connection"""
        await self.connection_manager.connect(websocket, user_id)
        
        try:
            # Start listening to Redis pub/sub
            await self.redis_pubsub.start(user_id, self._on_redis_message)
            
            while True:
                # Receive messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await self._handle_client_message(websocket, user_id, message)
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
        finally:
            await self.connection_manager.disconnect(websocket, user_id)
            await self.redis_pubsub.stop(user_id)
    
    async def _handle_client_message(self, websocket: WebSocket, user_id: UUID, message: dict):
        """Handle message from client"""
        msg_type = message.get("type")
        
        if msg_type == "SUBSCRIBE":
            streams = message.get("streams", [])
            filters = message.get("filters", {})
            await self.connection_manager.subscribe(user_id, streams, filters)
            await websocket.send_json({"type": "SUBSCRIBED", "streams": streams})
        
        elif msg_type == "UNSUBSCRIBE":
            streams = message.get("streams", [])
            await self.connection_manager.unsubscribe(user_id, streams)
            await websocket.send_json({"type": "UNSUBSCRIBED", "streams": streams})
        
        elif msg_type == "PING":
            await websocket.send_json({"type": "PONG", "timestamp": message.get("timestamp")})
    
    async def _on_redis_message(self, user_id: UUID, channel: str, message: dict):
        """Handle message from Redis pub/sub"""
        # Forward to WebSocket client
        await self.connection_manager.send_to_user(user_id, message)
