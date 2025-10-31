"""Redis Cache for Positions"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.utils.redis_client import VeloxRedisClient
from .config import settings

logger = logging.getLogger(__name__)

class PositionCache:
    def __init__(self):
        self.redis = VeloxRedisClient(settings.REDIS_URL)
    
    def cache_position(self, position_id: str, position_data: dict):
        key = f"position:{position_id}"
        self.redis.set_json(key, position_data, ex=3600)
    
    def get_position(self, position_id: str):
        key = f"position:{position_id}"
        return self.redis.get_json(key)
    
    def publish_update(self, position_data: dict):
        self.redis.publish("position-updates", position_data)
