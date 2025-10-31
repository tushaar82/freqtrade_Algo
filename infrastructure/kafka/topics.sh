#!/bin/bash
# VELOX Trading Platform - Kafka Topic Creation Script
# Created: 2025-10-31

KAFKA_BROKER="localhost:9092"

echo "Creating Kafka topics for VELOX Trading Platform..."

# Market Data Stream (high volume, partitioned by instrument)
kafka-topics --create \
  --bootstrap-server $KAFKA_BROKER \
  --topic market-data-stream \
  --partitions 10 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config compression.type=lz4 \
  --if-not-exists

# Signal Events (partitioned by strategy)
kafka-topics --create \
  --bootstrap-server $KAFKA_BROKER \
  --topic signal-events \
  --partitions 5 \
  --replication-factor 1 \
  --config retention.ms=7776000000 \
  --if-not-exists

# Order Events (partitioned by strategy, long retention for audit)
kafka-topics --create \
  --bootstrap-server $KAFKA_BROKER \
  --topic order-events \
  --partitions 5 \
  --replication-factor 1 \
  --config retention.ms=31536000000 \
  --if-not-exists

# Position Events (partitioned by strategy)
kafka-topics --create \
  --bootstrap-server $KAFKA_BROKER \
  --topic position-events \
  --partitions 5 \
  --replication-factor 1 \
  --config retention.ms=31536000000 \
  --if-not-exists

# System Events (single partition for ordering)
kafka-topics --create \
  --bootstrap-server $KAFKA_BROKER \
  --topic system-events \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=31536000000 \
  --if-not-exists

echo "Kafka topics created successfully!"
echo ""
echo "Listing all topics:"
kafka-topics --list --bootstrap-server $KAFKA_BROKER
