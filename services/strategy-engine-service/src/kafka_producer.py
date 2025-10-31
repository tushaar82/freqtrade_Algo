"""
Kafka Producer for Signal Events
VELOX Strategy Engine Service
"""
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.utils.kafka_producer import VeloxKafkaProducer
from .config import settings

logger = logging.getLogger(__name__)


class SignalEventProducer:
    """Produce signal events to Kafka"""
    
    def __init__(self):
        self.producer = VeloxKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
    
    def publish_signal(self, signal_event: dict[str, Any]) -> None:
        """
        Publish signal event to Kafka
        
        Args:
            signal_event: Signal event dictionary
        """
        try:
            self.producer.send_event(
                topic="signal-events",
                event_type=signal_event["signal_type"],
                payload=signal_event,
                key=signal_event["strategy_id"]  # Partition by strategy
            )
            logger.debug(f"Published signal: {signal_event['signal_id']}")
        except Exception as e:
            logger.error(f"Failed to publish signal: {e}")
    
    def close(self) -> None:
        """Close producer"""
        self.producer.close()
