# Feature Specification: Multi-Strategy Trading Platform

**Feature Branch**: `1-multi-strategy-platform`  
**Created**: 2025-10-31  
**Status**: Draft  
**Input**: User description: "application which is capable to run multiple strategies over multiple stocks or options with realtime dashboard and analysis. ability to paper trade before going live, multibroker use broker adapter for timebeing use smartapi. the strategies can be multi timeframe with fixed or trailing stoploss. use 2 accounts one for admin and other for investor.design such a way that i can easily plugnplay strategies, the dashbaord must contain realtime charts and analysis. the charts will be pnl chart. price vs trailing stoploss chart. all data stored in database with detailed logging indicators, signals, and trailing Stoploss."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Strategy Deployment & Execution (Priority: P1)

An admin user deploys a new trading strategy (e.g., momentum-based) on selected stocks/options with defined parameters (timeframe, stop-loss type, position sizing). The system executes the strategy in paper trading mode, monitoring entry/exit signals, tracking P&L, and logging all decisions.

**Why this priority**: Core trading functionality - without strategy execution, the platform has no value. This is the MVP foundation.

**Independent Test**: Deploy a simple moving average crossover strategy on 2-3 stocks in paper trading mode. Verify signals are generated, orders are simulated, P&L is calculated, and all data is logged to database.

**Acceptance Scenarios**:

1. **Given** admin is logged in, **When** they create a new strategy with parameters (name, instruments, timeframe, stop-loss type, position size), **Then** strategy is saved and ready for deployment
2. **Given** a strategy is configured, **When** admin activates it in paper trading mode, **Then** system subscribes to real-time market data for selected instruments and begins monitoring
3. **Given** strategy is running, **When** entry conditions are met, **Then** system generates buy signal, simulates order placement, logs signal with indicators, and updates position tracking
4. **Given** position is open, **When** stop-loss (fixed or trailing) is hit, **Then** system generates exit signal, simulates order closure, calculates P&L, and logs complete trade details
5. **Given** strategy is running, **When** multiple timeframes are configured, **Then** system correctly aggregates signals across timeframes before execution decision

---

### User Story 2 - Real-Time Dashboard & Monitoring (Priority: P1)

Admin and investor users view a real-time dashboard showing active strategies, current positions, P&L charts, and price vs trailing stop-loss visualization. Dashboard updates live as market data streams in and strategies execute trades.

**Why this priority**: Essential for monitoring and risk management. Users need immediate visibility into system performance and positions.

**Independent Test**: With strategies running, open dashboard and verify: (1) P&L chart updates in real-time, (2) price vs trailing stop-loss chart shows current price and dynamic stop levels, (3) position table shows all active trades, (4) strategy status indicators reflect current state.

**Acceptance Scenarios**:

1. **Given** user is logged in, **When** they access the dashboard, **Then** they see all active strategies with current status (running/paused/stopped)
2. **Given** strategies are executing, **When** a trade is opened/closed, **Then** dashboard immediately reflects position changes and updated P&L
3. **Given** dashboard is open, **When** viewing P&L chart, **Then** chart displays cumulative P&L over time with strategy-wise breakdown
4. **Given** position with trailing stop-loss exists, **When** viewing price vs stop-loss chart, **Then** chart shows current price line and dynamically adjusting stop-loss level
5. **Given** multiple strategies are running, **When** user filters by strategy or instrument, **Then** dashboard shows only relevant data

---

### User Story 3 - Multi-Broker Integration & Failover (Priority: P2)

Admin configures multiple broker connections (starting with SmartAPI) through a broker adapter pattern. System routes orders through configured brokers and handles broker-specific API differences transparently. If primary broker fails, system can route through backup broker.

**Why this priority**: Critical for production reliability per Constitution Principle IV, but can be implemented after core strategy execution is proven in paper trading.

**Independent Test**: Configure SmartAPI broker connection, execute paper trades through broker adapter. Verify adapter normalizes broker responses. Simulate broker API failure and verify graceful error handling.

**Acceptance Scenarios**:

1. **Given** admin is in broker configuration, **When** they add SmartAPI credentials and connection details, **Then** system validates connection and stores broker configuration
2. **Given** broker adapter is configured, **When** strategy generates order, **Then** adapter translates order to broker-specific format and simulates submission
3. **Given** multiple brokers are configured, **When** primary broker is unavailable, **Then** system logs error and continues paper trading (live failover in future phase)
4. **Given** broker responses are received, **When** adapter processes them, **Then** system normalizes data into unified format for strategy consumption

---

### User Story 4 - Paper Trading to Live Transition (Priority: P2)

After successful paper trading validation (minimum 30 days per Constitution), admin transitions a strategy from paper trading to live trading mode. System begins placing real orders through broker APIs while maintaining identical logging and monitoring.

**Why this priority**: Required for production deployment but only after paper trading proves strategy viability. Builds on P1 foundation.

**Independent Test**: Run strategy in paper trading for test period, review performance metrics, then switch to live mode with small capital. Verify real orders are placed, filled, and tracked identically to paper trading.

**Acceptance Scenarios**:

1. **Given** strategy has completed 30+ days paper trading, **When** admin reviews performance metrics (Sharpe ratio, max drawdown, win rate), **Then** system displays comprehensive validation report
2. **Given** validation report is satisfactory, **When** admin enables live trading mode, **Then** system prompts for confirmation and capital allocation limits
3. **Given** strategy is in live mode, **When** entry signal is generated, **Then** system performs pre-trade risk checks (margin, position limits, regulatory) and places real order via broker API
4. **Given** live order is placed, **When** broker confirms fill, **Then** system updates position tracking, logs execution details, and continues monitoring
5. **Given** live trading is active, **When** daily loss limit is breached, **Then** system automatically pauses strategy and sends multi-channel alerts

---

### User Story 5 - Strategy Plug-and-Play Architecture (Priority: P3)

Developers create new strategy modules following a defined interface/contract. Strategies are loaded dynamically without core system changes. Each strategy implements required methods (initialize, on_tick, calculate_signals, manage_positions) and declares its requirements (indicators, timeframes, instruments).

**Why this priority**: Enables scalability and rapid strategy development, but core platform must be stable first. Can be refactored from initial hardcoded strategies.

**Independent Test**: Create a new strategy class implementing the strategy interface, place it in strategies directory, restart system. Verify strategy appears in admin UI and can be configured/deployed without code changes to core platform.

**Acceptance Scenarios**:

1. **Given** strategy interface is defined, **When** developer creates new strategy class, **Then** class implements all required methods (initialize, on_tick, calculate_signals, manage_positions, cleanup)
2. **Given** strategy class is complete, **When** placed in strategies directory, **Then** system auto-discovers and registers strategy on startup
3. **Given** strategy is registered, **When** admin views strategy list, **Then** new strategy appears with metadata (name, description, required parameters, supported instruments)
4. **Given** strategy is selected, **When** admin configures parameters, **Then** system validates parameters against strategy schema and enables deployment
5. **Given** multiple strategies are deployed, **When** they share instruments, **Then** system efficiently manages single market data subscription and distributes ticks to all strategies

---

### User Story 6 - Role-Based Access Control (Priority: P3)

System supports two user roles: Admin (full access to strategy configuration, broker setup, system settings) and Investor (read-only access to dashboard, P&L, positions). Users authenticate securely and see role-appropriate interfaces.

**Why this priority**: Important for multi-user environments but not critical for initial single-user deployment. Can be added after core functionality is stable.

**Independent Test**: Create admin and investor accounts. Login as admin and verify access to all features. Login as investor and verify read-only dashboard access with no configuration options.

**Acceptance Scenarios**:

1. **Given** system is initialized, **When** first admin account is created, **Then** admin can access all platform features
2. **Given** admin is logged in, **When** they create investor account, **Then** investor receives credentials and can login
3. **Given** investor is logged in, **When** they access dashboard, **Then** they see real-time P&L, positions, and charts but no configuration options
4. **Given** investor attempts to access admin features, **When** they navigate to restricted pages, **Then** system denies access and shows appropriate message
5. **Given** admin is logged in, **When** they modify strategy configuration, **Then** changes are immediately reflected in investor's dashboard view

---

### Edge Cases

- **What happens when market data feed disconnects during active trading?** System detects connection loss, pauses all strategies, logs event, sends critical alerts, and attempts reconnection. Positions remain tracked but no new orders until connection restored.

- **How does system handle partial order fills?** System tracks partial fills separately, updates position size incrementally, adjusts stop-loss levels based on filled quantity, and logs each fill event with timestamp and price.

- **What if trailing stop-loss calculation results in invalid price (below zero, outside circuit limits)?** System validates calculated stop-loss against exchange rules, clamps to valid range, logs validation event, and uses nearest valid price.

- **How are corporate actions (splits, bonuses, dividends) handled for open positions?** System subscribes to corporate action feeds, adjusts position quantities and prices automatically, recalculates stop-loss levels, and logs adjustment details.

- **What happens when database connection fails during trade execution?** System maintains in-memory state, queues log entries, continues critical operations (order management, risk checks), and flushes queued data when connection restored. Critical failure triggers alerts.

- **How does system handle clock drift or timestamp mismatches with exchange?** System uses NTP synchronization with NSE time servers (Constitution Principle III), validates timestamps on all incoming data, and rejects out-of-sequence messages.

- **What if strategy generates conflicting signals (buy and sell simultaneously)?** System prioritizes exit signals over entry signals, logs conflict event, and requires strategy to resolve ambiguity before execution.

- **How are multi-timeframe strategies synchronized?** System aligns timeframes to common boundaries (e.g., 5-min and 15-min both align on 15-min boundaries), ensures all required timeframe data is available before signal generation, and logs synchronization events.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support deployment of multiple trading strategies simultaneously, each with independent configuration (instruments, timeframes, stop-loss type, position sizing)
- **FR-002**: System MUST execute strategies in paper trading mode, simulating order placement and fill without real capital deployment
- **FR-003**: System MUST subscribe to real-time tick-by-tick market data for all instruments used by active strategies
- **FR-004**: System MUST calculate entry and exit signals based on strategy logic, indicator values, and multi-timeframe analysis
- **FR-005**: System MUST support both fixed stop-loss (absolute price/percentage) and trailing stop-loss (dynamic adjustment based on price movement)
- **FR-006**: System MUST integrate with broker APIs through an adapter pattern, starting with SmartAPI, normalizing broker-specific differences
- **FR-007**: System MUST provide real-time dashboard displaying active strategies, current positions, P&L metrics, and visual charts
- **FR-008**: System MUST generate P&L charts showing cumulative profit/loss over time with strategy-wise breakdown
- **FR-009**: System MUST generate price vs trailing stop-loss charts showing current price and dynamically adjusting stop levels for each position
- **FR-010**: System MUST store all trading data in database: orders, fills, positions, P&L, indicators, signals, stop-loss adjustments, and system events
- **FR-011**: System MUST support two user roles: Admin (full access) and Investor (read-only dashboard access)
- **FR-012**: System MUST authenticate users securely and enforce role-based access control
- **FR-013**: System MUST transition strategies from paper trading to live trading mode after validation period
- **FR-014**: System MUST perform pre-trade risk checks before placing live orders (margin, position limits, regulatory restrictions)
- **FR-015**: System MUST support plug-and-play strategy architecture allowing new strategies to be added without core system changes
- **FR-016**: System MUST handle multi-timeframe strategies, synchronizing data across timeframes before signal generation
- **FR-017**: System MUST log all strategy decisions, indicator calculations, signal generations, and order events with precise timestamps
- **FR-018**: System MUST detect and handle market data disconnections, partial order fills, and broker API failures gracefully
- **FR-019**: System MUST synchronize system clock with NSE time servers using NTP
- **FR-020**: System MUST send multi-channel alerts (email, SMS, Telegram) for critical events (strategy failures, loss limits, system errors)

### Key Entities

- **Strategy**: Represents a trading algorithm with configuration (name, instruments, timeframes, indicators, entry/exit rules, stop-loss type, position sizing rules, risk parameters)
- **Instrument**: Stock or option contract with metadata (symbol, exchange, lot size, tick size, circuit limits)
- **Position**: Open trade with details (instrument, entry price, quantity, current price, unrealized P&L, stop-loss level, entry timestamp)
- **Order**: Trade instruction with lifecycle (pending, submitted, acknowledged, filled, rejected, cancelled) and details (instrument, side, quantity, price, order type, timestamps)
- **Signal**: Strategy decision point with context (strategy, instrument, signal type [entry/exit], timestamp, indicator values, reasoning)
- **User**: System user with role (Admin/Investor), credentials, and access permissions
- **BrokerAdapter**: Integration module for specific broker API (SmartAPI initially) handling authentication, order translation, response normalization
- **MarketData**: Real-time tick data (instrument, timestamp, price, volume) and historical bars (OHLCV for multiple timeframes)
- **Indicator**: Technical indicator calculation (SMA, EMA, RSI, etc.) with parameters and values over time
- **Trade**: Completed transaction with full details (entry/exit prices, quantity, P&L, holding period, strategy, timestamps)

### Risk Management Requirements *(mandatory for trading features)*

- **RM-001**: Pre-trade risk checks MUST validate margin availability before order placement (live trading only)
- **RM-002**: Position limits MUST enforce maximum position size per strategy and overall portfolio limits
- **RM-003**: Kill switches MUST be implemented at strategy level (pause individual strategy), account level (pause all strategies), and portfolio level (emergency stop all trading)
- **RM-004**: Loss limits MUST trigger automatic trading suspension at Rs. 5000/- daily loss (configurable per strategy and portfolio)
- **RM-005**: Regulatory compliance MUST ensure SEBI circuit breaker enforcement, T2T stock restrictions, and GSM list checks before order placement
- **RM-006**: Stop-loss validation MUST ensure calculated stop-loss prices are within exchange-allowed ranges and circuit limits
- **RM-007**: Position sizing MUST calculate trade quantity based on volatility, stop-loss distance, and risk parameters to limit per-trade risk
- **RM-008**: Order validation MUST check instrument liquidity, market hours, and order type compatibility before submission

### Testing & Validation Requirements *(mandatory for trading features)*

- **TV-001**: Backtesting MUST include slippage modeling, STT (Securities Transaction Tax), GST, exchange fees, and broker commissions for realistic P&L calculation
- **TV-002**: Paper trading MUST run for minimum 30 days in live market conditions before any strategy is approved for live trading
- **TV-003**: Chaos testing MUST simulate broker API failures (connection loss, timeout, invalid responses), network outages, and bad data (missing ticks, out-of-sequence data, corrupt values)
- **TV-004**: Performance validation MUST verify live paper trading results match backtested expectations within 15% tolerance for key metrics (Sharpe ratio, max drawdown, win rate)
- **TV-005**: Integration testing MUST validate broker adapter correctly handles all order types, partial fills, rejections, and amendments
- **TV-006**: Load testing MUST verify system can handle 100+ concurrent strategies across 500+ instruments with sub-second latency
- **TV-007**: Data integrity testing MUST validate position reconciliation between internal tracking and broker-provided positions every 10 seconds
- **TV-008**: Failover testing MUST verify graceful degradation when market data feed disconnects or database connection fails

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin can deploy a new strategy from configuration to paper trading execution in under 5 minutes
- **SC-002**: System processes real-time market data ticks and generates signals with latency under 100ms (95th percentile)
- **SC-003**: Dashboard updates reflect position changes and P&L within 1 second of trade execution
- **SC-004**: System successfully completes 30-day paper trading period for a strategy with 100% uptime and complete data logging
- **SC-005**: Plug-and-play strategy architecture allows new strategy deployment without system restart or core code changes
- **SC-006**: Database contains complete audit trail with all indicators, signals, orders, and stop-loss adjustments queryable for analysis
- **SC-007**: Multi-timeframe strategies correctly synchronize data across timeframes with zero signal generation errors
- **SC-008**: System handles broker API failures gracefully with automatic reconnection within 30 seconds and zero data loss
- **SC-009**: Role-based access control prevents investor users from accessing 100% of admin-only features
- **SC-010**: Real-time charts (P&L, price vs stop-loss) render smoothly with updates every 1 second without UI lag
- **SC-011**: System transitions strategy from paper to live trading with identical execution logic and zero configuration drift
- **SC-012**: Pre-trade risk checks reject 100% of orders violating margin, position limits, or regulatory restrictions before broker submission
