"""
Redis Client Wrapper
VELOX Trading Platform
"""
import json
import logging
from typing import Any, Optional

import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)


class VeloxRedisClient:
    """Reusable Redis client with connection pooling"""
    
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self.url = url
        self.pool = ConnectionPool.from_url(url, decode_responses=True, max_connections=50)
        self.client = redis.Redis(connection_pool=self.pool)
        logger.info(f"Redis client initialized: {url}")
    
    def set_json(self, key: str, value: dict[str, Any], ex: Optional[int] = None) -> bool:
        """
        Set JSON value with optional expiration
        
        Args:
            key: Redis key
            value: Dictionary to store as JSON
            ex: Expiration in seconds (optional)
        
        Returns:
            True if successful
        """
        try:
            json_value = json.dumps(value)
            return self.client.set(key, json_value, ex=ex)
        except Exception as e:
            logger.error(f"Failed to set JSON key {key}: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[dict[str, Any]]:
        """
        Get JSON value
        
        Args:
            key: Redis key
        
        Returns:
            Dictionary if key exists, None otherwise
        """
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Failed to get JSON key {key}: {e}")
            return None
    
    def hset_dict(self, key: str, mapping: dict[str, Any]) -> int:
        """
        Set hash fields from dictionary
        
        Args:
            key: Redis hash key
            mapping: Dictionary of field-value pairs
        
        Returns:
            Number of fields added
        """
        try:
            # Convert values to strings
            str_mapping = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                          for k, v in mapping.items()}
            return self.client.hset(key, mapping=str_mapping)
        except Exception as e:
            logger.error(f"Failed to set hash {key}: {e}")
            return 0
    
    def hgetall_dict(self, key: str) -> dict[str, Any]:
        """
        Get all hash fields as dictionary
        
        Args:
            key: Redis hash key
        
        Returns:
            Dictionary of field-value pairs
        """
        try:
            data = self.client.hgetall(key)
            # Try to parse JSON values
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except json.JSONDecodeError:
                    result[k] = v
            return result
        except Exception as e:
            logger.error(f"Failed to get hash {key}: {e}")
            return {}
    
    def publish(self, channel: str, message: dict[str, Any]) -> int:
        """
        Publish message to channel
        
        Args:
            channel: Redis Pub/Sub channel
            message: Message dictionary
        
        Returns:
            Number of subscribers that received the message
        """
        try:
            json_message = json.dumps(message)
            return self.client.publish(channel, json_message)
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return 0
    
    def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    def close(self) -> None:
        """Close Redis connection"""
        self.client.close()
        logger.info("Redis client closed")
