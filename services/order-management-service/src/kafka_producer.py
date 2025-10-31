"""
Kafka Producer for Order Events
VELOX Order Management Service
"""
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.utils.kafka_producer import VeloxKafkaProducer
from .config import settings

logger = logging.getLogger(__name__)


class OrderEventProducer:
    """Produce order events to Kafka"""
    
    def __init__(self):
        self.producer = VeloxKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
    
    def publish_order_event(self, order_event: dict[str, Any]) -> None:
        try:
            self.producer.send_event(
                topic="order-events",
                event_type=order_event["status"],
                payload=order_event,
                key=order_event["strategy_id"]
            )
            logger.debug(f"Published order event: {order_event['order_id']}")
        except Exception as e:
            logger.error(f"Failed to publish order event: {e}")
    
    def close(self) -> None:
        self.producer.close()
