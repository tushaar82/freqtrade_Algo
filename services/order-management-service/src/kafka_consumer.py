"""
Kafka Consumer for Signal Events
VELOX Order Management Service
"""
import logging
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.utils.kafka_consumer import VeloxKafkaConsumer
from .config import settings

logger = logging.getLogger(__name__)


class SignalEventConsumer:
    """Consume signal events from Kafka"""
    
    def __init__(self, callback: Callable[[dict], None]):
        self.consumer = VeloxKafkaConsumer(
            topics=["signal-events"],
            group_id="order-management-service",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        self.callback = callback
    
    def start(self) -> None:
        logger.info("Starting signal event consumer...")
        self.consumer.consume(self.callback)
    
    def stop(self) -> None:
        self.consumer.close()
