"""Kafka Consumer for Analytics"""
import logging
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.utils.kafka_consumer import VeloxKafkaConsumer
from .config import settings

logger = logging.getLogger(__name__)

class AnalyticsEventConsumer:
    def __init__(self, callback: Callable):
        self.consumer = VeloxKafkaConsumer(
            topics=["order-events", "position-events"],
            group_id="analytics-service",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        self.callback = callback
    
    def start(self):
        logger.info("Starting analytics event consumer...")
        self.consumer.consume(self.callback)
    
    def stop(self):
        self.consumer.close()
