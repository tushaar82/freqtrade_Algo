"""
Redis Pub/Sub Manager for WebSocket
VELOX Trading Platform
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Callable
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from shared.utils.redis_client import VeloxRedisClient
from ..config import settings

logger = logging.getLogger(__name__)


class RedisPubSubManager:
    """Manage Redis pub/sub for WebSocket streaming"""
    
    def __init__(self):
        self.redis = VeloxRedisClient(settings.REDIS_URL)
        self.subscribers: dict[UUID, asyncio.Task] = {}
        self.channels = ["position-updates", "pnl-updates", "signal-updates", "order-updates"]
    
    async def start(self, user_id: UUID, callback: Callable):
        """Start listening to Redis channels"""
        task = asyncio.create_task(self._listen(user_id, callback))
        self.subscribers[user_id] = task
    
    async def stop(self, user_id: UUID):
        """Stop listening"""
        if user_id in self.subscribers:
            task = self.subscribers[user_id]
            task.cancel()
            del self.subscribers[user_id]
    
    async def _listen(self, user_id: UUID, callback: Callable):
        """Listen to Redis pub/sub channels"""
        pubsub = self.redis.client.pubsub()
        
        try:
            # Subscribe to channels
            for channel in self.channels:
                pubsub.subscribe(channel)
            
            logger.info(f"Listening to Redis channels for user {user_id}")
            
            while True:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        channel = message['channel']
                        await callback(user_id, channel, data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON from Redis: {message['data']}")
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy loop
        
        except asyncio.CancelledError:
            logger.info(f"Redis listener cancelled for user {user_id}")
        except Exception as e:
            logger.error(f"Redis listener error: {e}", exc_info=True)
        finally:
            pubsub.unsubscribe()
            pubsub.close()
