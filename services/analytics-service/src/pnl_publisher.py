"""P&L Publisher to Redis"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.utils.redis_client import VeloxRedisClient
from .config import settings

logger = logging.getLogger(__name__)

class PnLPublisher:
    def __init__(self):
        self.redis = VeloxRedisClient(settings.REDIS_URL)
    
    def publish_pnl_update(self, pnl_data: dict):
        """Publish P&L update to Redis"""
        try:
            self.redis.publish("pnl-updates", pnl_data)
            logger.debug(f"Published P&L update for strategy {pnl_data.get('strategy_id')}")
        except Exception as e:
            logger.error(f"Failed to publish P&L update: {e}")
