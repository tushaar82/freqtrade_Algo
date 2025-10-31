# Kafka Event Schemas

## Overview

All events use JSON format with the following common structure:

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "timestamp": "ISO 8601 datetime",
  "version": "1.0",
  "payload": { ... }
}
```

## Topics

### market-data-stream

**Partitioning**: By `instrument_id`  
**Retention**: 7 days  
**Replication Factor**: 3

**Event Schema**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "MARKET_TICK",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "version": "1.0",
  "payload": {
    "instrument_id": "uuid",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "price": 2456.75,
    "volume": 125000,
    "bid_price": 2456.50,
    "ask_price": 2457.00,
    "bid_quantity": 500,
    "ask_quantity": 750,
    "open_interest": null
  }
}
```

---

### signal-events

**Partitioning**: By `strategy_id`  
**Retention**: 90 days  
**Replication Factor**: 3

**Event Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "SIGNAL_GENERATED",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "version": "1.0",
  "payload": {
    "signal_id": "uuid",
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "instrument_id": "uuid",
    "symbol": "RELIANCE",
    "signal_type": "ENTRY_LONG",
    "strength": 0.85,
    "indicators": {
      "sma_short": 2455.30,
      "sma_long": 2450.10,
      "rsi": 35.2,
      "volume": 125000
    },
    "reasoning": "SMA short crossed above SMA long with RSI oversold",
    "recommended_quantity": 10,
    "recommended_price": 2456.75
  }
}
```

---

### order-events

**Partitioning**: By `strategy_id`  
**Retention**: 1 year  
**Replication Factor**: 3

**Event Types**:
- `ORDER_CREATED`
- `ORDER_SUBMITTED`
- `ORDER_ACKNOWLEDGED`
- `ORDER_PARTIAL_FILLED`
- `ORDER_FILLED`
- `ORDER_REJECTED`
- `ORDER_CANCELLED`

**Event Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "ORDER_FILLED",
  "timestamp": "2025-10-31T15:30:50.456+05:30",
  "version": "1.0",
  "payload": {
    "order_id": "uuid",
    "strategy_id": "uuid",
    "instrument_id": "uuid",
    "symbol": "RELIANCE",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 10,
    "filled_quantity": 10,
    "average_fill_price": 2456.80,
    "status": "FILLED",
    "mode": "PAPER",
    "broker_order_id": "123456789",
    "fills": [
      {
        "fill_id": "uuid",
        "quantity": 10,
        "price": 2456.80,
        "timestamp": "2025-10-31T15:30:50.456+05:30"
      }
    ]
  }
}
```

---

### position-events

**Partitioning**: By `strategy_id`  
**Retention**: 1 year  
**Replication Factor**: 3

**Event Types**:
- `POSITION_OPENED`
- `POSITION_UPDATED`
- `POSITION_CLOSED`

**Event Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "POSITION_OPENED",
  "timestamp": "2025-10-31T15:30:50.456+05:30",
  "version": "1.0",
  "payload": {
    "position_id": "uuid",
    "strategy_id": "uuid",
    "instrument_id": "uuid",
    "symbol": "RELIANCE",
    "side": "LONG",
    "quantity": 10,
    "entry_price": 2456.80,
    "stop_loss_price": 2408.18,
    "take_profit_price": 2580.00,
    "mode": "PAPER"
  }
}
```

---

### system-events

**Partitioning**: Single partition (ordered)  
**Retention**: 1 year  
**Replication Factor**: 3

**Event Types**:
- `SERVICE_STARTED`
- `SERVICE_STOPPED`
- `SERVICE_HEALTH_CHECK`
- `CIRCUIT_BREAKER_TRIGGERED`
- `LOSS_LIMIT_BREACHED`
- `BROKER_CONNECTION_LOST`
- `BROKER_CONNECTION_RESTORED`

**Event Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "LOSS_LIMIT_BREACHED",
  "timestamp": "2025-10-31T15:30:00.000+05:30",
  "version": "1.0",
  "payload": {
    "service": "risk-management-service",
    "severity": "CRITICAL",
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "limit_type": "DAILY_LOSS",
    "limit_value": 5000.00,
    "current_value": 5100.00,
    "action_taken": "STRATEGY_PAUSED",
    "message": "Daily loss limit of Rs. 5000 breached, strategy automatically paused"
  }
}
```

---

## Event Producers

| Service | Topics Produced |
|---------|----------------|
| Market Data Service | market-data-stream |
| Strategy Engine Service | signal-events |
| Order Management Service | order-events |
| Position Tracking Service | position-events |
| Risk Management Service | system-events |
| All Services | system-events (health checks) |

## Event Consumers

| Service | Topics Consumed |
|---------|----------------|
| Strategy Engine Service | market-data-stream |
| Order Management Service | signal-events |
| Position Tracking Service | order-events |
| Risk Management Service | signal-events, order-events |
| Analytics Service | order-events, position-events |
| Dashboard API Service | All topics (for WebSocket streaming) |
| Alert Service | system-events |

## Event Ordering Guarantees

- **market-data-stream**: Ordered per instrument (partitioned by instrument_id)
- **signal-events**: Ordered per strategy (partitioned by strategy_id)
- **order-events**: Ordered per strategy (partitioned by strategy_id)
- **position-events**: Ordered per strategy (partitioned by strategy_id)
- **system-events**: Globally ordered (single partition)

## Error Handling

All services implement:
- **Retry logic**: Exponential backoff for transient failures
- **Dead letter queue**: Failed events moved to `{topic}-dlq` after 3 retries
- **Idempotency**: Event consumers use `event_id` to deduplicate

## Schema Evolution

- **Backward compatible**: New fields added as optional
- **Version field**: Consumers check version and handle accordingly
- **Schema registry**: Consider Confluent Schema Registry for production
