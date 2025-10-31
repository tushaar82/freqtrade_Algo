# WebSocket Streams - Dashboard Real-Time Updates

## Connection

**Endpoint**: `ws://localhost:8000/ws/dashboard`  
**Protocol**: WebSocket  
**Authentication**: JWT token in query parameter or header

**Connection URL**:
```
ws://localhost:8000/ws/dashboard?token={jwt_access_token}
```

**Alternative (Header)**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'AUTH',
    token: 'jwt_access_token'
  }));
};
```

## Message Format

All messages follow this structure:

```json
{
  "type": "string",
  "timestamp": "ISO 8601 datetime",
  "data": { ... }
}
```

## Client → Server Messages

### Subscribe to Streams

```json
{
  "type": "SUBSCRIBE",
  "streams": ["positions", "pnl", "signals", "orders", "system_events"],
  "filters": {
    "strategy_id": "uuid",  // Optional: filter by strategy
    "mode": "PAPER"         // Optional: PAPER or LIVE
  }
}
```

### Unsubscribe from Streams

```json
{
  "type": "UNSUBSCRIBE",
  "streams": ["signals"]
}
```

### Ping (Keep-Alive)

```json
{
  "type": "PING"
}
```

## Server → Client Messages

### Pong (Keep-Alive Response)

```json
{
  "type": "PONG",
  "timestamp": "2025-10-31T15:30:00.000+05:30"
}
```

### Position Update

```json
{
  "type": "POSITION_UPDATE",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "data": {
    "position_id": "uuid",
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "instrument": {
      "id": "uuid",
      "symbol": "RELIANCE",
      "exchange": "NSE"
    },
    "side": "LONG",
    "quantity": 10,
    "entry_price": 2456.80,
    "current_price": 2458.50,
    "stop_loss_price": 2408.18,
    "unrealized_pnl": 17.00,
    "status": "OPEN",
    "mode": "PAPER"
  }
}
```

### P&L Update

```json
{
  "type": "PNL_UPDATE",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "data": {
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "realized_pnl": 1250.50,
    "unrealized_pnl": 175.30,
    "total_pnl": 1425.80,
    "daily_pnl": 325.50,
    "mode": "PAPER",
    "breakdown": {
      "gross_pnl": 1500.00,
      "transaction_costs": 74.20,
      "net_pnl": 1425.80
    }
  }
}
```

### Signal Generated

```json
{
  "type": "SIGNAL_GENERATED",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "data": {
    "signal_id": "uuid",
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "instrument": {
      "symbol": "RELIANCE",
      "exchange": "NSE"
    },
    "signal_type": "ENTRY_LONG",
    "strength": 0.85,
    "indicators": {
      "sma_short": 2455.30,
      "sma_long": 2450.10,
      "rsi": 35.2
    },
    "reasoning": "SMA short crossed above SMA long with RSI oversold",
    "recommended_quantity": 10,
    "recommended_price": 2456.75
  }
}
```

### Order Update

```json
{
  "type": "ORDER_UPDATE",
  "timestamp": "2025-10-31T15:30:50.456+05:30",
  "data": {
    "order_id": "uuid",
    "strategy_id": "uuid",
    "instrument": {
      "symbol": "RELIANCE",
      "exchange": "NSE"
    },
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 10,
    "filled_quantity": 10,
    "average_fill_price": 2456.80,
    "status": "FILLED",
    "mode": "PAPER",
    "created_at": "2025-10-31T15:30:45.123+05:30",
    "filled_at": "2025-10-31T15:30:50.456+05:30"
  }
}
```

### Strategy Status Update

```json
{
  "type": "STRATEGY_STATUS",
  "timestamp": "2025-10-31T15:30:00.000+05:30",
  "data": {
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "status": "RUNNING",
    "mode": "PAPER",
    "active_positions": 3,
    "total_pnl": 1425.80,
    "last_signal_time": "2025-10-31T15:29:45.123+05:30"
  }
}
```

### System Event

```json
{
  "type": "SYSTEM_EVENT",
  "timestamp": "2025-10-31T15:30:00.000+05:30",
  "data": {
    "event_type": "LOSS_LIMIT_BREACHED",
    "severity": "CRITICAL",
    "strategy_id": "uuid",
    "strategy_name": "MA Crossover",
    "message": "Daily loss limit of Rs. 5000 breached, strategy automatically paused",
    "action_taken": "STRATEGY_PAUSED"
  }
}
```

### Market Data Tick (Optional Stream)

```json
{
  "type": "MARKET_TICK",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "data": {
    "instrument_id": "uuid",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "price": 2456.75,
    "volume": 125000,
    "bid_price": 2456.50,
    "ask_price": 2457.00
  }
}
```

### Error Message

```json
{
  "type": "ERROR",
  "timestamp": "2025-10-31T15:30:00.000+05:30",
  "data": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": null
  }
}
```

## Connection Lifecycle

### 1. Connect

Client establishes WebSocket connection with JWT token.

### 2. Authenticate

Server validates token and sends confirmation:

```json
{
  "type": "CONNECTED",
  "timestamp": "2025-10-31T15:30:00.000+05:30",
  "data": {
    "user_id": "uuid",
    "role": "ADMIN",
    "session_id": "uuid"
  }
}
```

### 3. Subscribe

Client subscribes to desired streams.

### 4. Receive Updates

Server pushes real-time updates as they occur.

### 5. Keep-Alive

Client sends PING every 30 seconds, server responds with PONG.

### 6. Disconnect

Client closes connection or server closes on inactivity (5 minutes without PING).

## Error Codes

| Code | Description |
|------|-------------|
| UNAUTHORIZED | Invalid or expired token |
| FORBIDDEN | User role does not have access to requested data |
| INVALID_MESSAGE | Malformed message format |
| SUBSCRIPTION_ERROR | Failed to subscribe to stream |
| RATE_LIMIT_EXCEEDED | Too many messages sent |

## Rate Limiting

- **Max connections per user**: 5
- **Max messages per second**: 10
- **Max subscriptions per connection**: 20

## Reconnection Strategy

Client should implement exponential backoff:

```javascript
let reconnectDelay = 1000; // Start with 1 second
const maxDelay = 30000; // Max 30 seconds

function connect() {
  const ws = new WebSocket('ws://localhost:8000/ws/dashboard?token=' + token);
  
  ws.onclose = () => {
    setTimeout(() => {
      reconnectDelay = Math.min(reconnectDelay * 2, maxDelay);
      connect();
    }, reconnectDelay);
  };
  
  ws.onopen = () => {
    reconnectDelay = 1000; // Reset on successful connection
  };
}
```

## Example Client Implementation (React)

```typescript
import { useEffect, useState } from 'react';

interface WebSocketMessage {
  type: string;
  timestamp: string;
  data: any;
}

export function useDashboardWebSocket(token: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [pnl, setPnl] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);

  useEffect(() => {
    const websocket = new WebSocket(
      `ws://localhost:8000/ws/dashboard?token=${token}`
    );

    websocket.onopen = () => {
      console.log('WebSocket connected');
      // Subscribe to streams
      websocket.send(JSON.stringify({
        type: 'SUBSCRIBE',
        streams: ['positions', 'pnl', 'signals', 'orders']
      }));
    };

    websocket.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'POSITION_UPDATE':
          setPositions(prev => {
            const index = prev.findIndex(p => p.position_id === message.data.position_id);
            if (index >= 0) {
              const updated = [...prev];
              updated[index] = message.data;
              return updated;
            }
            return [...prev, message.data];
          });
          break;
        
        case 'PNL_UPDATE':
          setPnl(message.data);
          break;
        
        case 'SIGNAL_GENERATED':
          setSignals(prev => [message.data, ...prev].slice(0, 50)); // Keep last 50
          break;
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      // Implement reconnection logic
    };

    setWs(websocket);

    // Cleanup
    return () => {
      websocket.close();
    };
  }, [token]);

  return { positions, pnl, signals };
}
```

## Security Considerations

- **Token expiration**: Clients must handle token refresh and reconnect
- **Message validation**: Server validates all incoming messages
- **Rate limiting**: Prevents abuse and DoS attacks
- **Connection limits**: Max 5 connections per user prevents resource exhaustion
- **CORS**: Configure allowed origins in production
