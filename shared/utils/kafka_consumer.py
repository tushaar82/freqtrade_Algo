"""
Kafka Consumer Wrapper
VELOX Trading Platform
"""
import json
import logging
from typing import Callable, Optional

from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class VeloxKafkaConsumer:
    """Reusable Kafka consumer with JSON deserialization"""
    
    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: str = "localhost:9092",
        auto_offset_reset: str = "earliest"
    ):
        self.topics = topics
        self.group_id = group_id
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            max_poll_records=100
        )
        logger.info(f"Kafka consumer initialized: {group_id} -> {topics}")
    
    def consume(self, callback: Callable[[dict], None]) -> None:
        """
        Consume messages and invoke callback
        
        Args:
            callback: Function to process each message
        """
        try:
            for message in self.consumer:
                try:
                    event = message.value
                    callback(event)
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}")
            raise
        finally:
            self.close()
    
    def close(self) -> None:
        """Close consumer connection"""
        self.consumer.close()
        logger.info("Kafka consumer closed")
