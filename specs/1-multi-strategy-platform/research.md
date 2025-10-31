# Research: Multi-Strategy Trading Platform

**Date**: 2025-10-31  
**Purpose**: Technology decisions, architecture patterns, and best practices for microservices-based trading platform

## Technology Stack Decisions

### Backend Framework: FastAPI

**Decision**: Use FastAPI 0.104+ for all microservices

**Rationale**:
- **Performance**: ASGI-based, handles 10,000+ requests/second (meets performance goals)
- **Async support**: Native async/await for non-blocking I/O (critical for real-time data)
- **Type safety**: Pydantic integration provides runtime validation and OpenAPI generation
- **WebSocket support**: Built-in WebSocket for dashboard real-time updates
- **Developer experience**: Auto-generated API docs, fast development cycles

**Alternatives Considered**:
- **Flask**: Synchronous by default, requires gevent/eventlet for async (more complex)
- **Django**: Too heavyweight for microservices, REST framework adds overhead
- **aiohttp**: Lower-level, requires more boilerplate for REST APIs

**Implementation Notes**:
- Use `fastapi.BackgroundTasks` for non-blocking operations
- Implement dependency injection for database sessions, Kafka producers
- Use `fastapi.WebSocket` for dashboard streaming
- Enable CORS middleware for React frontend

---

### Message Broker: Apache Kafka

**Decision**: Use Apache Kafka 3.5+ for event streaming

**Rationale**:
- **Event sourcing**: Immutable log provides audit trail (Constitution Principle I)
- **Replay capability**: Can replay events for backtesting, debugging, disaster recovery
- **Scalability**: Handles millions of messages/day, horizontal scaling via partitions
- **Durability**: Configurable replication factor ensures zero data loss
- **Decoupling**: Services communicate via events, not direct calls (fault isolation)

**Alternatives Considered**:
- **RabbitMQ**: Message queue model, not event log (no replay, no audit trail)
- **Redis Streams**: Limited retention, no multi-datacenter replication
- **AWS Kinesis**: Cloud-only, vendor lock-in

**Topic Design**:
```
market-data-stream (partitioned by instrument_id)
├── Key: instrument_id
└── Value: {timestamp, price, volume, ...}

order-events (partitioned by strategy_id)
├── Key: order_id
└── Value: {order_id, strategy_id, state, timestamp, ...}

signal-events (partitioned by strategy_id)
├── Key: signal_id
└── Value: {strategy_id, instrument_id, signal_type, indicators, ...}

system-events (single partition for ordering)
└── Value: {event_type, service, severity, message, timestamp}
```

**Configuration**:
- Replication factor: 3 (production)
- Retention: 7 days for market data, 90 days for orders/signals, 1 year for system events
- Compression: LZ4 for balance of speed and size
- Acks: `all` for order events (durability), `1` for market data (speed)

---

### Caching Layer: Redis

**Decision**: Use Redis 7+ for real-time data and session management

**Rationale**:
- **Sub-millisecond latency**: In-memory storage meets <100ms signal generation requirement
- **Data structures**: Sorted sets for time-series, hashes for positions, pub/sub for notifications
- **Persistence**: RDB + AOF for durability without sacrificing speed
- **Sentinel**: High availability with automatic failover

**Use Cases**:
1. **Latest tick cache**: `HSET instrument:{id} price volume timestamp`
2. **Active positions**: `HSET position:{strategy_id} {instrument_id} {quantity, entry_price, ...}`
3. **Strategy state**: `HSET strategy:{id} status last_signal_time indicators`
4. **Session management**: `SETEX session:{token} 3600 {user_data}`
5. **Rate limiting**: `INCR ratelimit:{user_id}:{endpoint} EX 60`

**Alternatives Considered**:
- **Memcached**: No data structures, no persistence (insufficient for position tracking)
- **PostgreSQL**: Too slow for sub-millisecond reads (100x slower than Redis)

**Configuration**:
- Persistence: RDB every 5 minutes + AOF every second
- Eviction policy: `allkeys-lru` for cache, `noeviction` for critical data (positions)
- Sentinel: 3-node cluster for automatic failover

---

### Database: PostgreSQL

**Decision**: Use PostgreSQL 15+ for persistent storage and audit trails

**Rationale**:
- **ACID compliance**: Critical for financial data integrity (Constitution Principle II)
- **JSONB support**: Flexible schema for strategy parameters, indicator values
- **Partitioning**: Table partitioning for time-series data (trades, ticks)
- **Full-text search**: Search audit logs, strategy descriptions
- **Mature ecosystem**: SQLAlchemy ORM, Alembic migrations, pgAdmin

**Schema Design Principles**:
- **Audit tables**: Immutable insert-only tables for trades, orders, signals
- **Partitioning**: Partition trades/ticks by month for query performance
- **Indexes**: B-tree on timestamps, GIN on JSONB columns
- **Constraints**: Foreign keys, check constraints for data integrity

**Alternatives Considered**:
- **MongoDB**: No ACID transactions (unacceptable for financial data)
- **TimescaleDB**: PostgreSQL extension for time-series, but adds complexity
- **MySQL**: Weaker JSON support, less mature partitioning

**Configuration**:
- Connection pooling: PgBouncer with 100 connections per service
- Replication: Streaming replication with 1 standby (production)
- Backup: Daily full backup + WAL archiving for point-in-time recovery

---

### Frontend: React 18 + TailwindCSS

**Decision**: Use React 18+ with TailwindCSS 3+ for dashboard

**Rationale**:
- **Component model**: Reusable components for charts, tables, forms
- **Concurrent features**: useTransition for smooth UI during data updates
- **Ecosystem**: Rich charting libraries (Recharts, Chart.js), WebSocket hooks
- **Developer experience**: Fast refresh, TypeScript support, large community

**UI Framework**: TailwindCSS for utility-first styling, rapid prototyping

**Charting**: 
- **Recharts**: Declarative, React-native, good for P&L line charts
- **Chart.js**: More features, better performance for real-time updates

**State Management**: 
- **React Context**: Global auth state, user preferences
- **SWR/React Query**: Server state caching, automatic refetching
- **Local state**: useState for component-specific state

**Alternatives Considered**:
- **Vue.js**: Smaller ecosystem, less TypeScript adoption
- **Angular**: Too heavyweight, steeper learning curve
- **Svelte**: Smaller ecosystem, less mature tooling

---

## Architecture Patterns

### Microservices Communication

**Pattern**: Event-driven architecture with Kafka + REST APIs

**Design**:
1. **Async events** (Kafka): Market data, signals, order state changes, system events
2. **Sync APIs** (REST): Dashboard queries, strategy configuration, user management
3. **WebSocket**: Real-time dashboard updates (positions, P&L, charts)

**Service Boundaries**:
- **Market Data Service**: Ingests ticks from broker APIs, publishes to Kafka
- **Strategy Engine Service**: Consumes market data, generates signals, publishes to Kafka
- **Order Management Service**: Consumes signals, manages order lifecycle, publishes order events
- **Risk Management Service**: Validates orders before submission, enforces limits
- **Position Tracking Service**: Maintains position state, reconciles with broker
- **Analytics Service**: Calculates P&L, metrics, performance statistics
- **Dashboard API Service**: Aggregates data for frontend, manages WebSocket connections
- **Alert Service**: Monitors events, sends notifications via email/SMS/Telegram

**Communication Flow**:
```
Market Data Service → Kafka (market-data-stream)
                    ↓
Strategy Engine Service → Kafka (signal-events)
                        ↓
Risk Management Service (validates)
                        ↓
Order Management Service → Broker API
                        ↓ Kafka (order-events)
Position Tracking Service → Redis (positions)
                          ↓
Dashboard API Service → WebSocket → React Frontend
```

---

### Broker Adapter Pattern

**Pattern**: Strategy pattern with abstract base class

**Design**:
```python
class BrokerAdapter(ABC):
    @abstractmethod
    async def connect(self, credentials: dict) -> bool:
        pass
    
    @abstractmethod
    async def place_order(self, order: Order) -> OrderResponse:
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        pass
    
    @abstractmethod
    async def subscribe_market_data(self, instruments: List[str]) -> AsyncIterator[Tick]:
        pass

class SmartAPIAdapter(BrokerAdapter):
    # SmartAPI-specific implementation
    pass

class ZerodhaKiteAdapter(BrokerAdapter):
    # Zerodha Kite-specific implementation
    pass
```

**Benefits**:
- **Pluggable**: Add new brokers without changing core logic
- **Testable**: Mock adapter for unit tests, paper trading
- **Failover**: Switch adapters at runtime if broker fails

**Implementation Notes**:
- Use factory pattern to instantiate adapters based on configuration
- Implement retry logic with exponential backoff for API calls
- Normalize broker responses to common data models (Pydantic)
- Handle broker-specific quirks (rate limits, order types) in adapter

---

### Strategy Plug-and-Play Architecture

**Pattern**: Plugin architecture with dynamic loading

**Design**:
```python
class StrategyBase(ABC):
    @abstractmethod
    def initialize(self, config: dict) -> None:
        pass
    
    @abstractmethod
    def on_tick(self, tick: Tick) -> None:
        pass
    
    @abstractmethod
    def calculate_signals(self) -> List[Signal]:
        pass
    
    @abstractmethod
    def manage_positions(self, positions: List[Position]) -> List[Action]:
        pass

# strategies/moving_average.py
class MovingAverageCrossover(StrategyBase):
    def initialize(self, config: dict):
        self.short_window = config['short_window']
        self.long_window = config['long_window']
    
    def on_tick(self, tick: Tick):
        # Update indicators
        pass
    
    def calculate_signals(self) -> List[Signal]:
        # Generate buy/sell signals
        pass
```

**Dynamic Loading**:
```python
import importlib
import inspect

def load_strategies(strategy_dir: Path) -> Dict[str, Type[StrategyBase]]:
    strategies = {}
    for file in strategy_dir.glob("*.py"):
        module = importlib.import_module(f"strategies.{file.stem}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, StrategyBase) and obj != StrategyBase:
                strategies[name] = obj
    return strategies
```

**Benefits**:
- **No restart**: Drop new strategy file, system auto-discovers
- **Isolation**: Strategy errors don't crash engine
- **Versioning**: Multiple versions of same strategy can coexist

---

### Real-Time Dashboard Updates

**Pattern**: WebSocket with Redis Pub/Sub

**Design**:
```python
# Dashboard API Service
@app.websocket("/ws/dashboard")
async def dashboard_stream(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("positions", "pnl", "signals")
    
    async for message in pubsub.listen():
        if message['type'] == 'message':
            await websocket.send_json(message['data'])
```

**Frontend**:
```typescript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

**Benefits**:
- **Low latency**: Sub-second updates from event to UI
- **Scalability**: Redis Pub/Sub handles thousands of subscribers
- **Simplicity**: No polling, no HTTP overhead

---

## Testing Strategy

### Unit Testing

**Framework**: pytest 7+ with pytest-asyncio, pytest-mock

**Coverage Target**: 80%+ for all services

**Approach**:
- **Mock external dependencies**: Kafka, Redis, PostgreSQL, broker APIs
- **Test business logic**: Signal generation, position calculation, risk checks
- **Test edge cases**: Partial fills, API timeouts, invalid data

**Example**:
```python
@pytest.mark.asyncio
async def test_signal_generation():
    strategy = MovingAverageCrossover(config={'short_window': 5, 'long_window': 20})
    ticks = [Tick(price=100), Tick(price=101), ...]
    
    for tick in ticks:
        strategy.on_tick(tick)
    
    signals = strategy.calculate_signals()
    assert len(signals) == 1
    assert signals[0].type == SignalType.BUY
```

---

### Integration Testing

**Framework**: pytest with Testcontainers (Docker-based)

**Approach**:
- **Spin up real dependencies**: Kafka, Redis, PostgreSQL in Docker containers
- **Test service interactions**: Market data → Strategy engine → Order management
- **Test data flow**: Verify events published to Kafka, data written to PostgreSQL

**Example**:
```python
@pytest.fixture(scope="module")
def kafka_container():
    with KafkaContainer() as kafka:
        yield kafka

def test_market_data_to_signal_flow(kafka_container):
    # Publish market data to Kafka
    # Verify signal event published by strategy engine
    pass
```

---

### Chaos Engineering

**Framework**: Custom scripts + pytest

**Scenarios**:
1. **Kafka broker failure**: Kill Kafka container, verify services reconnect
2. **Redis failure**: Stop Redis, verify services degrade gracefully (use PostgreSQL fallback)
3. **Broker API timeout**: Mock slow API responses, verify retry logic
4. **Network partition**: Simulate network split, verify data consistency

**Example**:
```python
def test_kafka_failure_recovery():
    # Start services
    # Kill Kafka container
    # Verify services enter degraded state
    # Restart Kafka
    # Verify services reconnect and resume processing
    pass
```

---

### End-to-End Testing

**Framework**: Cypress for frontend, pytest for backend

**Scenarios**:
1. **Strategy deployment**: Admin creates strategy → Strategy appears in dashboard
2. **Paper trading**: Strategy generates signal → Position opens → P&L updates
3. **Role-based access**: Investor cannot access strategy configuration

---

## Performance Optimization

### Market Data Processing

**Optimization**: Batch processing with async I/O

**Approach**:
- Use `asyncio.gather()` to process multiple ticks concurrently
- Batch Kafka writes (100 messages per batch)
- Use Redis pipeline for bulk writes

**Expected Performance**: 10,000 ticks/second per service instance

---

### Signal Generation Latency

**Optimization**: Pre-compute indicators, use Redis for latest values

**Approach**:
- Maintain rolling window of indicator values in memory
- Use Redis sorted sets for time-series data (O(log N) lookup)
- Avoid database queries in hot path

**Expected Latency**: <100ms (95th percentile)

---

### Dashboard Update Latency

**Optimization**: Redis Pub/Sub + WebSocket

**Approach**:
- Position updates published to Redis Pub/Sub immediately
- Dashboard API subscribes to Redis channels
- WebSocket streams updates to frontend (no polling)

**Expected Latency**: <1 second from event to UI

---

## Security Considerations

### Authentication

**Approach**: JWT tokens with refresh tokens

**Implementation**:
- Login endpoint returns access token (15 min expiry) + refresh token (7 days)
- Access token stored in memory (React state)
- Refresh token stored in httpOnly cookie
- Middleware validates JWT on every request

---

### Authorization

**Approach**: Role-based access control (RBAC)

**Roles**:
- **Admin**: Full access (strategy config, broker setup, system settings)
- **Investor**: Read-only (dashboard, P&L, positions)

**Implementation**:
- JWT payload includes user role
- FastAPI dependency checks role before endpoint execution
- Frontend hides admin features for investor users

---

### API Security

**Measures**:
- **Rate limiting**: Redis-based rate limiter (100 requests/minute per user)
- **CORS**: Whitelist frontend origin
- **Input validation**: Pydantic models validate all inputs
- **SQL injection**: SQLAlchemy ORM prevents SQL injection
- **Secrets management**: Environment variables, never hardcode

---

## Deployment Strategy

### Development

**Approach**: Docker Compose with hot reload

**Services**: All microservices + Kafka + Redis + PostgreSQL in single docker-compose.yml

**Benefits**: One-command setup, consistent environment

---

### Production

**Approach**: Kubernetes with Helm charts

**Components**:
- **Kafka**: Strimzi operator for Kafka cluster management
- **Redis**: Redis Sentinel for high availability
- **PostgreSQL**: Patroni for automatic failover
- **Services**: Kubernetes Deployments with HPA (Horizontal Pod Autoscaler)
- **Ingress**: Nginx Ingress for routing, SSL termination

**Monitoring**: Prometheus + Grafana for metrics, ELK stack for logs

---

## Conclusion

Technology stack and architecture patterns selected to meet:
- **Performance**: <100ms signal latency, 10K ticks/second throughput
- **Reliability**: Event sourcing, service isolation, automatic failover
- **Scalability**: Horizontal scaling via Kafka partitions, Kubernetes HPA
- **Constitution compliance**: Audit trails, risk management, testing discipline
- **Developer experience**: Fast iteration, comprehensive testing, clear service boundaries

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts, quickstart.md)
