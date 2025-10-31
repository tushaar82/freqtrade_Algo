"""
Kafka Consumer for Market Data
VELOX Strategy Engine Service
"""
import json
import logging
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.utils.kafka_consumer import VeloxKafkaConsumer
from .config import settings

logger = logging.getLogger(__name__)


class MarketDataConsumer:
    """Consume market data from Kafka"""
    
    def __init__(self, callback: Callable[[dict], None]):
        self.consumer = VeloxKafkaConsumer(
            topics=["market-data-stream"],
            group_id="strategy-engine-service",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        self.callback = callback
    
    def start(self) -> None:
        """Start consuming market data"""
        logger.info("Starting market data consumer...")
        self.consumer.consume(self.callback)
    
    def stop(self) -> None:
        """Stop consumer"""
        self.consumer.close()
