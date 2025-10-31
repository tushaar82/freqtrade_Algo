# Data Model: Multi-Strategy Trading Platform

**Date**: 2025-10-31  
**Purpose**: Entity schemas, relationships, and database design for trading platform

## Entity Relationship Overview

```
User (1) ──── (N) Strategy
Strategy (1) ──── (N) StrategyInstrument
Strategy (1) ──── (N) Position
Strategy (1) ──── (N) Order
Strategy (1) ──── (N) Signal
Strategy (1) ──── (N) Trade

Instrument (1) ──── (N) StrategyInstrument
Instrument (1) ──── (N) Position
Instrument (1) ──── (N) Order
Instrument (1) ──── (N) MarketDataTick

Position (1) ──── (N) Order
Position (1) ──── (1) Trade (when closed)

BrokerAdapter (1) ──── (N) BrokerAccount
BrokerAccount (1) ──── (N) Order
```

## Core Entities

### User

**Purpose**: System users with role-based access control

**Fields**:
- `id`: UUID (PK)
- `email`: String (unique, indexed)
- `password_hash`: String
- `full_name`: String
- `role`: Enum (ADMIN, INVESTOR)
- `is_active`: Boolean
- `created_at`: Timestamp
- `last_login_at`: Timestamp (nullable)

**Validation Rules**:
- Email must be valid format
- Password must be hashed with bcrypt
- Role must be ADMIN or INVESTOR
- Email must be unique

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

**Relationships**:
- One user owns many strategies (if ADMIN)
- One user has many sessions

---

### Strategy

**Purpose**: Trading strategy configuration and state

**Fields**:
- `id`: UUID (PK)
- `name`: String (unique per user)
- `description`: Text (nullable)
- `owner_id`: UUID (FK → User.id)
- `strategy_type`: String (e.g., "MovingAverageCrossover", "Momentum")
- `config`: JSONB (strategy-specific parameters)
- `status`: Enum (DRAFT, PAPER_TRADING, LIVE, PAUSED, STOPPED)
- `mode`: Enum (PAPER, LIVE)
- `risk_params`: JSONB (position_size_pct, max_positions, stop_loss_pct)
- `created_at`: Timestamp
- `activated_at`: Timestamp (nullable)
- `deactivated_at`: Timestamp (nullable)

**Config Schema** (JSONB):
```json
{
  "timeframes": ["5m", "15m", "1h"],
  "indicators": {
    "sma_short": 5,
    "sma_long": 20,
    "rsi_period": 14
  },
  "entry_rules": {
    "sma_crossover": true,
    "rsi_threshold": 30
  },
  "exit_rules": {
    "stop_loss_type": "trailing",  // or "fixed"
    "stop_loss_pct": 2.0,
    "trailing_stop_pct": 1.5,
    "take_profit_pct": 5.0
  }
}
```

**Risk Params Schema** (JSONB):
```json
{
  "position_size_pct": 2.0,  // % of capital per trade
  "max_positions": 5,
  "max_daily_loss": 5000,  // Rs.
  "max_weekly_loss": 15000,
  "max_monthly_loss": 50000
}
```

**Validation Rules**:
- Name must be unique per user
- Status transitions: DRAFT → PAPER_TRADING → LIVE (or PAUSED/STOPPED)
- Mode cannot change from LIVE to PAPER (only PAPER → LIVE)
- Config must match strategy_type schema
- Risk params must have positive values

**Indexes**:
- PRIMARY KEY (id)
- INDEX (owner_id, status)
- INDEX (status, mode)

**Relationships**:
- One strategy belongs to one user
- One strategy has many strategy_instruments
- One strategy has many positions
- One strategy has many orders
- One strategy has many signals

---

### Instrument

**Purpose**: Stock or option contract metadata

**Fields**:
- `id`: UUID (PK)
- `symbol`: String (unique, e.g., "RELIANCE", "NIFTY25NOV24000CE")
- `exchange`: Enum (NSE, BSE, MCX, NFO)
- `instrument_type`: Enum (EQUITY, FUTURE, CALL_OPTION, PUT_OPTION)
- `lot_size`: Integer
- `tick_size`: Decimal
- `circuit_limit_upper`: Decimal (nullable)
- `circuit_limit_lower`: Decimal (nullable)
- `expiry_date`: Date (nullable, for F&O)
- `strike_price`: Decimal (nullable, for options)
- `is_active`: Boolean
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Validation Rules**:
- Symbol must be unique per exchange
- Lot size must be positive
- Tick size must be positive
- Circuit limits must be positive if set
- Expiry date required for F&O
- Strike price required for options

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (symbol, exchange)
- INDEX (exchange, instrument_type, is_active)
- INDEX (expiry_date) for F&O

**Relationships**:
- One instrument has many strategy_instruments
- One instrument has many positions
- One instrument has many market_data_ticks

---

### StrategyInstrument

**Purpose**: Many-to-many relationship between strategies and instruments

**Fields**:
- `id`: UUID (PK)
- `strategy_id`: UUID (FK → Strategy.id)
- `instrument_id`: UUID (FK → Instrument.id)
- `is_active`: Boolean
- `added_at`: Timestamp

**Validation Rules**:
- (strategy_id, instrument_id) must be unique

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (strategy_id, instrument_id)
- INDEX (strategy_id, is_active)

---

### Position

**Purpose**: Open or closed trading position

**Fields**:
- `id`: UUID (PK)
- `strategy_id`: UUID (FK → Strategy.id)
- `instrument_id`: UUID (FK → Instrument.id)
- `side`: Enum (LONG, SHORT)
- `quantity`: Integer
- `entry_price`: Decimal
- `current_price`: Decimal
- `stop_loss_price`: Decimal
- `take_profit_price`: Decimal (nullable)
- `unrealized_pnl`: Decimal
- `status`: Enum (OPEN, CLOSED)
- `opened_at`: Timestamp
- `closed_at`: Timestamp (nullable)
- `mode`: Enum (PAPER, LIVE)

**Validation Rules**:
- Quantity must be positive
- Entry price must be positive
- Stop loss must be below entry for LONG, above for SHORT
- Status transitions: OPEN → CLOSED (one-way)
- Closed_at must be set when status = CLOSED

**Indexes**:
- PRIMARY KEY (id)
- INDEX (strategy_id, status)
- INDEX (instrument_id, status)
- INDEX (opened_at DESC) for time-series queries

**Relationships**:
- One position belongs to one strategy
- One position belongs to one instrument
- One position has many orders
- One position has one trade (when closed)

**State Transitions**:
```
OPEN ──(stop_loss_hit or take_profit_hit or manual_close)──> CLOSED
```

---

### Order

**Purpose**: Order instruction with lifecycle tracking

**Fields**:
- `id`: UUID (PK)
- `strategy_id`: UUID (FK → Strategy.id)
- `instrument_id`: UUID (FK → Instrument.id)
- `position_id`: UUID (FK → Position.id, nullable for entry orders)
- `broker_order_id`: String (nullable, from broker)
- `side`: Enum (BUY, SELL)
- `order_type`: Enum (MARKET, LIMIT, STOP_LOSS, STOP_LOSS_MARKET)
- `quantity`: Integer
- `price`: Decimal (nullable for MARKET orders)
- `trigger_price`: Decimal (nullable for STOP_LOSS orders)
- `status`: Enum (PENDING, SUBMITTED, ACKNOWLEDGED, PARTIAL_FILLED, FILLED, REJECTED, CANCELLED)
- `filled_quantity`: Integer
- `average_fill_price`: Decimal (nullable)
- `rejection_reason`: Text (nullable)
- `mode`: Enum (PAPER, LIVE)
- `created_at`: Timestamp
- `submitted_at`: Timestamp (nullable)
- `filled_at`: Timestamp (nullable)
- `updated_at`: Timestamp

**Validation Rules**:
- Quantity must be positive
- Price must be positive if set
- Filled quantity <= quantity
- Status transitions must follow state machine
- Broker order ID required for LIVE mode when SUBMITTED

**Indexes**:
- PRIMARY KEY (id)
- INDEX (strategy_id, status)
- INDEX (position_id)
- INDEX (broker_order_id) for reconciliation
- INDEX (created_at DESC)

**Relationships**:
- One order belongs to one strategy
- One order belongs to one instrument
- One order may belong to one position
- One order has many order_fills

**State Machine**:
```
PENDING ──(submit)──> SUBMITTED ──(broker_ack)──> ACKNOWLEDGED
                                                      │
                                                      ├──(partial_fill)──> PARTIAL_FILLED
                                                      │                         │
                                                      ├──(full_fill)────────────┴──> FILLED
                                                      │
                                                      ├──(reject)──> REJECTED
                                                      │
                                                      └──(cancel)──> CANCELLED
```

---

### OrderFill

**Purpose**: Individual fill events for orders (partial or full)

**Fields**:
- `id`: UUID (PK)
- `order_id`: UUID (FK → Order.id)
- `fill_quantity`: Integer
- `fill_price`: Decimal
- `fill_timestamp`: Timestamp
- `broker_fill_id`: String (nullable)

**Validation Rules**:
- Fill quantity must be positive
- Fill price must be positive
- Sum of fills for order <= order quantity

**Indexes**:
- PRIMARY KEY (id)
- INDEX (order_id, fill_timestamp)

---

### Signal

**Purpose**: Strategy-generated trading signal

**Fields**:
- `id`: UUID (PK)
- `strategy_id`: UUID (FK → Strategy.id)
- `instrument_id`: UUID (FK → Instrument.id)
- `signal_type`: Enum (ENTRY_LONG, ENTRY_SHORT, EXIT_LONG, EXIT_SHORT)
- `strength`: Decimal (0.0 to 1.0, signal confidence)
- `indicators`: JSONB (indicator values at signal time)
- `reasoning`: Text (human-readable explanation)
- `generated_at`: Timestamp
- `executed`: Boolean
- `order_id`: UUID (FK → Order.id, nullable)

**Indicators Schema** (JSONB):
```json
{
  "sma_short": 105.5,
  "sma_long": 102.3,
  "rsi": 35.2,
  "volume": 1250000,
  "price": 106.8
}
```

**Validation Rules**:
- Strength must be between 0.0 and 1.0
- Indicators must be valid JSON
- If executed, order_id must be set

**Indexes**:
- PRIMARY KEY (id)
- INDEX (strategy_id, generated_at DESC)
- INDEX (instrument_id, signal_type, generated_at)
- GIN INDEX (indicators) for JSONB queries

**Relationships**:
- One signal belongs to one strategy
- One signal belongs to one instrument
- One signal may create one order

---

### Trade

**Purpose**: Completed trade with full P&L calculation

**Fields**:
- `id`: UUID (PK)
- `strategy_id`: UUID (FK → Strategy.id)
- `instrument_id`: UUID (FK → Instrument.id)
- `position_id`: UUID (FK → Position.id)
- `side`: Enum (LONG, SHORT)
- `entry_order_id`: UUID (FK → Order.id)
- `exit_order_id`: UUID (FK → Order.id)
- `quantity`: Integer
- `entry_price`: Decimal
- `exit_price`: Decimal
- `gross_pnl`: Decimal
- `transaction_costs`: Decimal (brokerage + STT + GST + exchange fees)
- `net_pnl`: Decimal
- `holding_period_seconds`: Integer
- `exit_reason`: Enum (STOP_LOSS, TAKE_PROFIT, TRAILING_STOP, MANUAL, STRATEGY_SIGNAL)
- `opened_at`: Timestamp
- `closed_at`: Timestamp
- `mode`: Enum (PAPER, LIVE)

**Validation Rules**:
- Quantity must be positive
- Gross PNL = (exit_price - entry_price) * quantity * (1 if LONG else -1)
- Net PNL = gross_pnl - transaction_costs
- Closed_at must be after opened_at

**Indexes**:
- PRIMARY KEY (id)
- INDEX (strategy_id, closed_at DESC)
- INDEX (instrument_id, closed_at DESC)
- INDEX (mode, closed_at DESC)

**Relationships**:
- One trade belongs to one strategy
- One trade belongs to one instrument
- One trade belongs to one position
- One trade has one entry order
- One trade has one exit order

---

### MarketDataTick

**Purpose**: Real-time market data tick (time-series)

**Fields**:
- `id`: UUID (PK)
- `instrument_id`: UUID (FK → Instrument.id)
- `timestamp`: Timestamp with timezone
- `price`: Decimal
- `volume`: Integer
- `bid_price`: Decimal (nullable)
- `ask_price`: Decimal (nullable)
- `bid_quantity`: Integer (nullable)
- `ask_quantity`: Integer (nullable)
- `open_interest`: Integer (nullable, for F&O)

**Validation Rules**:
- Price must be positive
- Volume must be non-negative
- Timestamp must be in exchange timezone (Asia/Kolkata)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (instrument_id, timestamp DESC)

**Partitioning**: Partition by month for query performance
```sql
CREATE TABLE market_data_ticks (
  ...
) PARTITION BY RANGE (timestamp);

CREATE TABLE market_data_ticks_2025_10 PARTITION OF market_data_ticks
  FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

**Relationships**:
- One tick belongs to one instrument

**Note**: High-volume table, consider retention policy (e.g., 90 days)

---

### BrokerAdapter

**Purpose**: Broker integration configuration

**Fields**:
- `id`: UUID (PK)
- `name`: String (unique, e.g., "SmartAPI", "ZerodhaKite")
- `adapter_class`: String (Python class name)
- `is_active`: Boolean
- `config_schema`: JSONB (required configuration fields)
- `created_at`: Timestamp

**Config Schema Example** (JSONB):
```json
{
  "api_key": {"type": "string", "required": true},
  "client_id": {"type": "string", "required": true},
  "password": {"type": "string", "required": true, "secret": true},
  "totp_secret": {"type": "string", "required": false, "secret": true}
}
```

**Validation Rules**:
- Name must be unique
- Adapter class must exist in codebase
- Config schema must be valid JSON Schema

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (name)

**Relationships**:
- One broker adapter has many broker accounts

---

### BrokerAccount

**Purpose**: User's broker account credentials

**Fields**:
- `id`: UUID (PK)
- `user_id`: UUID (FK → User.id)
- `broker_adapter_id`: UUID (FK → BrokerAdapter.id)
- `account_name`: String
- `credentials`: JSONB (encrypted)
- `is_primary`: Boolean
- `is_active`: Boolean
- `last_connected_at`: Timestamp (nullable)
- `created_at`: Timestamp

**Credentials Schema** (JSONB, encrypted at rest):
```json
{
  "api_key": "encrypted_value",
  "client_id": "encrypted_value",
  "password": "encrypted_value",
  "totp_secret": "encrypted_value"
}
```

**Validation Rules**:
- Credentials must match broker adapter config schema
- Only one primary account per user per broker
- Credentials must be encrypted with Fernet (symmetric encryption)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (user_id, is_active)
- INDEX (broker_adapter_id)

**Relationships**:
- One broker account belongs to one user
- One broker account belongs to one broker adapter
- One broker account has many orders (in LIVE mode)

---

## Redis Data Structures

### Latest Tick Cache

**Key**: `tick:{instrument_id}`  
**Type**: Hash  
**Fields**:
```
price: 106.8
volume: 1250000
timestamp: 1698765432
bid_price: 106.7
ask_price: 106.9
```

**TTL**: 1 hour (auto-refresh on updates)

---

### Active Positions

**Key**: `position:{strategy_id}:{instrument_id}`  
**Type**: Hash  
**Fields**:
```
quantity: 100
entry_price: 105.5
current_price: 106.8
stop_loss_price: 104.0
unrealized_pnl: 130.0
status: OPEN
```

**TTL**: None (persist until position closed)

---

### Strategy State

**Key**: `strategy:{strategy_id}:state`  
**Type**: Hash  
**Fields**:
```
status: RUNNING
last_signal_time: 1698765432
active_positions: 3
total_pnl: 2500.75
indicators: {"sma_short": 105.5, "sma_long": 102.3}
```

**TTL**: None (persist while strategy active)

---

### Session Management

**Key**: `session:{token}`  
**Type**: String (JSON)  
**Value**:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "ADMIN",
  "created_at": 1698765432
}
```

**TTL**: 3600 seconds (1 hour)

---

## Kafka Event Schemas

### Market Data Event

**Topic**: `market-data-stream`  
**Key**: `instrument_id`  
**Value**:
```json
{
  "instrument_id": "uuid",
  "timestamp": "2025-10-31T15:30:45.123+05:30",
  "price": 106.8,
  "volume": 1250000,
  "bid_price": 106.7,
  "ask_price": 106.9,
  "bid_quantity": 500,
  "ask_quantity": 750
}
```

---

### Signal Event

**Topic**: `signal-events`  
**Key**: `signal_id`  
**Value**:
```json
{
  "signal_id": "uuid",
  "strategy_id": "uuid",
  "instrument_id": "uuid",
  "signal_type": "ENTRY_LONG",
  "strength": 0.85,
  "indicators": {
    "sma_short": 105.5,
    "sma_long": 102.3,
    "rsi": 35.2
  },
  "reasoning": "SMA crossover with RSI oversold",
  "generated_at": "2025-10-31T15:30:45.123+05:30"
}
```

---

### Order Event

**Topic**: `order-events`  
**Key**: `order_id`  
**Value**:
```json
{
  "order_id": "uuid",
  "strategy_id": "uuid",
  "instrument_id": "uuid",
  "event_type": "ORDER_FILLED",
  "status": "FILLED",
  "filled_quantity": 100,
  "average_fill_price": 106.8,
  "timestamp": "2025-10-31T15:30:50.456+05:30"
}
```

---

### System Event

**Topic**: `system-events`  
**Key**: null (ordered by partition)  
**Value**:
```json
{
  "event_type": "SERVICE_HEALTH",
  "service": "strategy-engine-service",
  "severity": "INFO",
  "message": "Service healthy, processing 1500 ticks/sec",
  "timestamp": "2025-10-31T15:30:00.000+05:30"
}
```

---

## Database Migrations

**Tool**: Alembic (SQLAlchemy migration tool)

**Migration Strategy**:
1. **Version control**: Each migration has unique version ID
2. **Rollback support**: Down migrations for every up migration
3. **Data migrations**: Separate data migrations from schema migrations
4. **Testing**: Test migrations on staging before production

**Example Migration**:
```python
# alembic/versions/001_create_users_table.py
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'INVESTOR'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

---

## Data Retention Policies

| Entity | Retention Period | Rationale |
|--------|------------------|-----------|
| MarketDataTick | 90 days | High volume, historical data in separate archive |
| Signal | 1 year | Audit trail, strategy analysis |
| Order | 5 years | Regulatory compliance, tax reporting |
| Trade | 5 years | Regulatory compliance, tax reporting |
| Position | 5 years | Audit trail |
| User | Indefinite | Account data |
| Strategy | Indefinite | Configuration history |

**Archive Strategy**:
- Move old market data ticks to cold storage (S3/MinIO) after 90 days
- Keep aggregated OHLCV bars indefinitely for backtesting

---

## Conclusion

Data model supports:
- **Constitution compliance**: Audit trails, immutable order/trade records
- **Performance**: Redis for real-time data, PostgreSQL partitioning for time-series
- **Scalability**: Kafka event sourcing, horizontal scaling
- **Flexibility**: JSONB for strategy config, plug-and-play architecture
- **Data integrity**: Foreign keys, check constraints, state machine validation

**Next Steps**: Generate API contracts and quickstart guide
