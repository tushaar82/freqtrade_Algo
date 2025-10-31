"""Kafka Producer"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.utils.kafka_producer import VeloxKafkaProducer
from .config import settings

logger = logging.getLogger(__name__)

class PositionEventProducer:
    def __init__(self):
        self.producer = VeloxKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    
    def publish_position_event(self, event: dict):
        try:
            self.producer.send_event("position-events", event["status"], event, key=event["strategy_id"])
        except Exception as e:
            logger.error(f"Failed to publish position event: {e}")
    
    def close(self):
        self.producer.close()
