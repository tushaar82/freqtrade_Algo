"""
Kafka Producer Wrapper
VELOX Trading Platform
"""
import json
import logging
from typing import Any, Optional
from uuid import uuid4

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class VeloxKafkaProducer:
    """Reusable Kafka producer with JSON serialization"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=5,
            compression_type='lz4'
        )
        logger.info(f"Kafka producer initialized: {bootstrap_servers}")
    
    def send_event(
        self,
        topic: str,
        event_type: str,
        payload: dict[str, Any],
        key: Optional[str] = None,
        version: str = "1.0"
    ) -> None:
        """
        Send event to Kafka topic
        
        Args:
            topic: Kafka topic name
            event_type: Event type identifier
            payload: Event payload data
            key: Partition key (optional)
            version: Event schema version
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": payload.get("timestamp"),
            "version": version,
            "payload": payload
        }
        
        try:
            future = self.producer.send(topic, value=event, key=key)
            future.get(timeout=10)  # Block until sent
            logger.debug(f"Event sent to {topic}: {event_type}")
        except KafkaError as e:
            logger.error(f"Failed to send event to {topic}: {e}")
            raise
    
    def flush(self) -> None:
        """Flush pending messages"""
        self.producer.flush()
    
    def close(self) -> None:
        """Close producer connection"""
        self.producer.close()
        logger.info("Kafka producer closed")
