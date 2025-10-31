# Tasks: Multi-Strategy Trading Platform

**Input**: Design documents from `/specs/1-multi-strategy-platform/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5, US6)
- Include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create root project structure with services/, frontend/, infrastructure/, shared/, tests/ directories
- [X] T002 [P] Initialize infrastructure/docker-compose.yml with PostgreSQL, Redis, Kafka, Zookeeper services
- [X] T003 [P] Create infrastructure/postgres/init.sql with database initialization script
- [X] T004 [P] Create infrastructure/kafka/topics.sh script for Kafka topic creation
- [X] T005 [P] Create shared/schemas/ directories (events/, api/, database/)
- [X] T006 [P] Create .gitignore and root README.md

---

## Phase 2: Foundational (BLOCKS ALL USER STORIES)

### Database Foundation
- [X] T007 Create shared/schemas/database/base.py with SQLAlchemy Base
- [X] T008 [P] Create shared/schemas/database/user.py (User model)
- [X] T009 [P] Create shared/schemas/database/instrument.py (Instrument model)
- [X] T010 [P] Create shared/schemas/database/strategy.py (Strategy model)
- [X] T011 Setup Alembic in services/dashboard-api-service/
- [X] T012 Create migration 001_initial_schema.py (User, Instrument, Strategy tables)
- [ ] T013 Run migrations: `alembic upgrade head`

### Infrastructure
- [ ] T014 Start services: `docker-compose up -d`
- [ ] T015 Create Kafka topics (market-data-stream, signal-events, order-events, position-events, system-events)
- [X] T016 [P] Create shared/utils/kafka_producer.py
- [X] T017 [P] Create shared/utils/kafka_consumer.py
- [X] T018 [P] Create shared/utils/redis_client.py

### Authentication
- [X] T019 Create services/dashboard-api-service/src/auth/jwt.py
- [X] T020 Create services/dashboard-api-service/src/auth/password.py
- [X] T021 Create services/dashboard-api-service/src/auth/dependencies.py
- [X] T022 Create services/dashboard-api-service/src/middleware/cors.py

### Shared Models
- [X] T023 [P] Create shared/schemas/api/user.py (Pydantic models)
- [X] T024 [P] Create shared/schemas/api/strategy.py
- [X] T025 [P] Create shared/schemas/api/instrument.py
- [X] T026 [P] Create shared/schemas/events/market_data.py
- [X] T027 [P] Create shared/schemas/events/signal.py
- [X] T028 [P] Create shared/schemas/events/order.py

**Checkpoint**: Foundation ready

---

## Phase 3: US1 - Strategy Deployment & Execution (P1) 🎯 MVP

**Goal**: Deploy strategy in paper trading, generate signals, simulate orders, track P&L

**Test**: Deploy MA crossover on 2-3 stocks, verify signals/orders/P&L/logging

### Strategy Engine Service
- [X] T029 [P] [US1] Create services/strategy-engine-service/requirements.txt, Dockerfile, .env.example
- [X] T030 [US1] Create src/main.py, src/config.py
- [X] T031 [P] [US1] Create src/strategies/base.py (StrategyBase abstract class)
- [X] T032 [P] [US1] Create src/strategies/moving_average.py
- [X] T033 [US1] Create src/strategy_loader.py (dynamic loading)
- [X] T034 [US1] Create src/indicators.py (SMA, EMA, RSI)
- [X] T035 [US1] Create src/signal_generator.py
- [X] T036 [US1] Create src/kafka_consumer.py (market-data-stream)
- [X] T037 [US1] Create src/kafka_producer.py (signal-events)
- [X] T038 [US1] Create src/strategy_executor.py

### Order Management Service
- [X] T039 [P] [US1] Create services/order-management-service/requirements.txt, Dockerfile, .env.example
- [X] T040 [US1] Create src/main.py, src/config.py
- [X] T041 [US1] Create src/models/order.py (Order model)
- [X] T042 [US1] Create src/order_state_machine.py
- [X] T043 [US1] Create src/paper_trading.py (simulated execution)
- [X] T044 [US1] Create src/kafka_consumer.py (signal-events)
- [X] T045 [US1] Create src/kafka_producer.py (order-events)
- [X] T046 [US1] Create src/order_service.py

### Position Tracking Service
- [X] T047 [P] [US1] Create services/position-tracking-service/requirements.txt, Dockerfile, .env.example
- [X] T048 [US1] Create src/main.py, src/config.py
- [X] T049 [US1] Create src/models/position.py, src/models/trade.py
- [X] T050 [US1] Create src/position_calculator.py
- [X] T051 [US1] Create src/stop_loss_manager.py (fixed/trailing)
- [X] T052 [US1] Create src/kafka_consumer.py (order-events, market-data-stream)
- [X] T053 [US1] Create src/kafka_producer.py (position-events)
- [X] T054 [US1] Create src/redis_cache.py

### Dashboard API Service (US1 endpoints)
- [X] T055 [P] [US1] Create services/dashboard-api-service/requirements.txt, Dockerfile, .env.example
- [X] T056 [US1] Create src/main.py, src/config.py, src/database.py
- [X] T057 [US1] Create src/api/auth.py (POST /auth/login, /auth/refresh)
- [X] T058 [US1] Create src/api/strategies.py (CRUD + activate/pause/stop)
- [X] T059 [US1] Create src/api/positions.py (GET /positions, /positions/{id})
- [X] T060 [US1] Create src/services/strategy_service.py
- [X] T061 [US1] Create src/services/position_service.py

### Database & Seed
- [X] T062 [US1] Create migration 002_add_order_position_trade_tables.py
- [X] T063 [P] [US1] Create scripts/seed_data.py (admin, instruments, sample strategy)
- [ ] T064 [US1] Run seed: `python scripts/seed_data.py`

**Checkpoint**: US1 complete - strategies deploy, signals generate, orders simulate, positions track

---

## Phase 4: US2 - Real-Time Dashboard & Monitoring (P1)

**Goal**: Real-time dashboard with strategies, positions, P&L charts, price vs stop-loss visualization

**Test**: Open dashboard, verify P&L chart updates, price vs stop-loss chart, position table, strategy status

### Backend - WebSocket & Analytics
- [X] T065 [US2] Create services/dashboard-api-service/src/websocket/streams.py (/ws/dashboard)
- [X] T066 [US2] Create src/websocket/connection_manager.py
- [X] T067 [US2] Create src/websocket/redis_pubsub.py
- [X] T068 [US2] Update position-tracking-service to publish to Redis Pub/Sub
- [X] T069 [P] [US2] Create services/analytics-service/requirements.txt, Dockerfile, .env.example
- [X] T070 [US2] Create analytics-service src/main.py, src/config.py
- [X] T071 [US2] Create src/pnl_calculator.py
- [X] T072 [US2] Create src/metrics.py (Sharpe, Sortino, max drawdown)
- [X] T073 [US2] Create src/kafka_consumer.py (order-events, position-events)
- [X] T074 [US2] Create src/pnl_publisher.py (Redis Pub/Sub)
- [X] T075 [US2] Create dashboard-api-service src/api/analytics.py (GET /analytics/pnl, /metrics)

### Frontend - React Setup
- [X] T076 [P] [US2] Initialize frontend/ with create-react-app --template typescript
- [X] T077 [P] [US2] Install: axios, recharts, tailwindcss, @headlessui/react, lucide-react
- [X] T078 [P] [US2] Configure TailwindCSS
- [X] T079 [P] [US2] Create .env (REACT_APP_API_URL, REACT_APP_WS_URL)
- [X] T080 [US2] Create src/services/api.ts, src/services/websocket.ts, src/services/auth.ts
- [X] T081 [US2] Create src/contexts/AuthContext.tsx, src/contexts/WebSocketContext.tsx

### Frontend - Components
- [X] T082 [P] [US2] Create src/components/Auth/Login.tsx
- [X] T083 [P] [US2] Create src/components/Dashboard/StrategyList.tsx
- [X] T084 [P] [US2] Create src/components/Dashboard/PositionTable.tsx
- [X] T085 [P] [US2] Create src/components/Dashboard/PnLChart.tsx (Recharts)
- [X] T086 [P] [US2] Create src/components/Dashboard/PriceStopLossChart.tsx
- [X] T087 [P] [US2] Create src/components/common/Navbar.tsx, Sidebar.tsx
- [X] T088 [US2] Create src/hooks/useDashboardWebSocket.ts
- [X] T089 [US2] Create src/hooks/usePositions.ts, src/hooks/usePnL.ts

### Frontend - Pages
- [X] T090 [US2] Create src/pages/LoginPage.tsx
- [X] T091 [US2] Create src/pages/DashboardPage.tsx
- [X] T092 [US2] Create src/App.tsx (React Router, protected routes)
- [X] T093 [US2] Update src/index.tsx (providers)

**Checkpoint**: US1+US2 complete - dashboard shows real-time updates

---

## Phase 5: US3 - Multi-Broker Integration & Failover (P2)

**Goal**: Configure SmartAPI broker, route orders through adapter, handle API failures

**Test**: Configure SmartAPI, execute paper trades, verify adapter normalization, simulate failure

### Backend - Broker Adapter
- [ ] T094 [US3] Create order-management-service src/broker_adapter/base.py (BrokerAdapter abstract)
- [ ] T095 [US3] Create src/broker_adapter/smartapi.py (SmartAPI implementation)
- [ ] T096 [US3] Create src/broker_adapter/factory.py, src/broker_adapter/normalizer.py
- [ ] T097 [US3] Update src/order_service.py (use broker adapter)
- [ ] T098 [US3] Create src/broker_health.py
- [ ] T099 [US3] Create migration 003_add_broker_tables.py (BrokerAdapter, BrokerAccount)
- [ ] T100 [US3] Create shared/schemas/database/broker.py

### Backend - Broker API
- [ ] T101 [US3] Create dashboard-api-service src/api/brokers.py (CRUD endpoints)
- [ ] T102 [US3] Create src/services/broker_service.py

### Frontend - Broker Config
- [ ] T103 [P] [US3] Create src/components/Broker/BrokerList.tsx, BrokerAccountForm.tsx
- [ ] T104 [US3] Create src/pages/BrokerPage.tsx
- [ ] T105 [US3] Update src/App.tsx (/brokers route)

**Checkpoint**: US1+US2+US3 complete - broker adapter routes orders

---

## Phase 6: US4 - Paper Trading to Live Transition (P2)

**Goal**: Transition strategy from paper to live trading after 30-day validation

**Test**: Run paper trading, review metrics, switch to live, verify real orders

### Backend - Risk Management Service
- [ ] T106 [P] [US4] Create services/risk-management-service/requirements.txt, Dockerfile, .env.example
- [ ] T107 [US4] Create src/main.py, src/config.py
- [ ] T108 [US4] Create src/pre_trade_checks.py (margin, limits, circuit breakers)
- [ ] T109 [US4] Create src/position_limits.py, src/loss_limits.py (Rs. 5000/- daily)
- [ ] T110 [US4] Create src/kill_switch.py (strategy/account/portfolio stops)
- [ ] T111 [US4] Create src/sebi_compliance.py (T2T, GSM, circuit breakers)
- [ ] T112 [US4] Create src/kafka_consumer.py (signal-events), src/kafka_producer.py

### Backend - Live Trading
- [ ] T113 [US4] Update order-management-service src/order_service.py (live mode)
- [ ] T114 [US4] Update src/broker_adapter/smartapi.py (real orders)
- [ ] T115 [US4] Create src/order_reconciliation.py
- [ ] T116 [US4] Update position-tracking-service src/reconciliation.py

### Backend - Validation
- [ ] T117 [US4] Create analytics-service src/validation_report.py (30-day report)
- [ ] T118 [US4] Create dashboard-api-service src/api/validation.py (GET /strategies/{id}/validation-report)
- [ ] T119 [US4] Update src/api/strategies.py (mode transition validation)

### Frontend - Live Controls
- [ ] T120 [P] [US4] Create src/components/Strategy/ValidationReport.tsx, LiveTradingModal.tsx
- [ ] T121 [US4] Update src/components/Dashboard/StrategyList.tsx (live toggle)
- [ ] T122 [US4] Create src/components/RiskManagement/LossLimitMonitor.tsx

**Checkpoint**: US1-4 complete - paper to live transition with risk management

---

## Phase 7: US5 - Strategy Plug-and-Play (P3)

**Goal**: Developers create strategies, system auto-discovers and loads dynamically

**Test**: Create strategy class, place in strategies/, restart, verify appears in UI

### Backend - Strategy Interface
- [ ] T123 [US5] Update strategy-engine-service src/strategies/base.py (add metadata)
- [ ] T124 [US5] Update src/strategy_loader.py (hot-reload)
- [ ] T125 [US5] Create src/strategy_registry.py, src/strategy_validator.py
- [ ] T126 [P] [US5] Create src/strategies/momentum.py, mean_reversion.py (examples)

### Backend - Discovery API
- [ ] T127 [US5] Create dashboard-api-service src/api/strategy_types.py (GET /strategy-types, /strategy-types/{name}/schema)

### Frontend - Dynamic Config
- [ ] T128 [P] [US5] Create src/components/Strategy/StrategyTypeSelector.tsx, DynamicStrategyForm.tsx
- [ ] T129 [US5] Update src/components/Strategy/StrategyForm.tsx (dynamic form)
- [ ] T130 [US5] Create src/pages/StrategyPage.tsx

**Checkpoint**: US1-5 complete - plug-and-play strategies

---

## Phase 8: US6 - Role-Based Access Control (P3)

**Goal**: Admin and Investor roles with appropriate access

**Test**: Create admin/investor accounts, verify role-based access

### Backend - RBAC
- [ ] T131 [US6] Update dashboard-api-service src/auth/dependencies.py (role checks)
- [ ] T132 [US6] Update src/api/strategies.py, src/api/brokers.py (@require_admin)
- [ ] T133 [US6] Create src/api/users.py (user management)
- [ ] T134 [US6] Update src/api/auth.py (return role)

### Frontend - Role UI
- [ ] T135 [US6] Update src/contexts/AuthContext.tsx (add role)
- [ ] T136 [P] [US6] Create src/components/common/ProtectedRoute.tsx
- [ ] T137 [P] [US6] Create src/components/Admin/UserManagement.tsx
- [ ] T138 [US6] Update src/components/Dashboard/StrategyList.tsx (hide buttons for investor)
- [ ] T139 [US6] Update src/components/common/Sidebar.tsx (hide admin menu)
- [ ] T140 [US6] Create src/pages/AdminPage.tsx
- [ ] T141 [US6] Update src/App.tsx (role-based routes)

**Checkpoint**: All US1-6 complete

---

## Phase 9: Polish & Cross-Cutting

- [ ] T142 [P] Create services/alert-service/ (email/SMS/Telegram notifications)
- [ ] T143 [P] Create infrastructure/prometheus/prometheus.yml
- [ ] T144 [P] Create infrastructure/grafana/dashboards/ (system-health, trading-metrics)
- [ ] T145 [P] Add Prometheus /metrics endpoints to all services
- [ ] T146 [P] Create tests/integration/test_strategy_execution.py
- [ ] T147 [P] Create tests/integration/test_order_flow.py
- [ ] T148 [P] Create tests/e2e/cypress/integration/dashboard.spec.ts
- [ ] T149 [P] Create docs/API.md, docs/ARCHITECTURE.md
- [ ] T150 [P] Run quickstart.md validation

---

## Phase 10: Trading System Validation (Constitution-Mandated)

**Purpose**: Pre-production deployment gates

### Risk Management Validation
- [ ] T151 Pre-trade risk checks verified (margin, limits, price bands)
- [ ] T152 Kill switches tested (strategy, account, portfolio)
- [ ] T153 Loss limits validated (daily Rs. 5000/-, weekly, monthly)
- [ ] T154 Position sizing enforced
- [ ] T155 SEBI compliance checks tested

### Backtesting & Paper Trading
- [ ] T156 Backtesting with transaction costs (slippage, STT, GST, fees)
- [ ] T157 Walk-forward optimization validated
- [ ] T158 Paper trading initiated (30 days minimum)
- [ ] T159 Paper trading performance monitored
- [ ] T160 Edge cases handled (rejections, partial fills, API failures)

### Chaos Engineering
- [ ] T161 Broker API failure simulation
- [ ] T162 Network outage handling
- [ ] T163 Bad data injection scenarios
- [ ] T164 Broker failover verified
- [ ] T165 Position reconciliation under failure

### Monitoring & Alerting
- [ ] T166 Real-time dashboard operational
- [ ] T167 Multi-channel alerts configured (SMS, email, Telegram)
- [ ] T168 Automated emergency responses tested
- [ ] T169 Strategy degradation monitoring active

### Deployment Gates
- [ ] T170 Paper trading completed (30+ days)
- [ ] T171 All chaos tests passed
- [ ] T172 Risk management validation complete
- [ ] T173 Rollback procedure tested
- [ ] T174 Small capital deployment plan approved

**Checkpoint**: Constitution compliance verified - ready for staged production

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational
  - US1 (P1): Can start after Foundational
  - US2 (P1): Can start after Foundational (parallel with US1)
  - US3 (P2): Can start after Foundational
  - US4 (P2): Can start after Foundational
  - US5 (P3): Can start after Foundational
  - US6 (P3): Can start after Foundational
- **Polish (Phase 9)**: Depends on desired user stories
- **Validation (Phase 10)**: Depends on all user stories for production

### User Story Dependencies
- **US1**: Independent - core MVP
- **US2**: Independent - can develop in parallel with US1
- **US3**: Independent - broker adapter pattern
- **US4**: Requires US1 (strategy execution) + US3 (broker adapter)
- **US5**: Independent - refactors US1 strategy loading
- **US6**: Independent - adds RBAC layer

### Parallel Opportunities
- **Setup**: All tasks marked [P] can run in parallel
- **Foundational**: Database models, Kafka utils, Redis utils, shared schemas can run in parallel
- **US1+US2**: Can develop simultaneously (different services/components)
- **Within each US**: Tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (US1 + US2 Only)
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Strategy Execution)
4. Complete Phase 4: US2 (Dashboard)
5. **STOP and VALIDATE**: Test independently, deploy/demo

### Incremental Delivery
1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → Test → Deploy (MVP!)
3. Add US3 → Test → Deploy (Multi-broker)
4. Add US4 → Test → Deploy (Live trading)
5. Add US5 + US6 → Test → Deploy (Full platform)

### Parallel Team Strategy
With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational done:
   - Developer A: US1 (Strategy Engine, Order Management, Position Tracking)
   - Developer B: US2 (Analytics, Dashboard API, React Frontend)
   - Developer C: US3 (Broker Adapter)
3. Stories integrate independently

---

## Summary

- **Total Tasks**: 174
- **US1 Tasks**: 36 (T029-T064) - Strategy execution core
- **US2 Tasks**: 29 (T065-T093) - Real-time dashboard
- **US3 Tasks**: 12 (T094-T105) - Multi-broker integration
- **US4 Tasks**: 17 (T106-T122) - Live trading transition
- **US5 Tasks**: 8 (T123-T130) - Plug-and-play architecture
- **US6 Tasks**: 11 (T131-T141) - Role-based access control
- **Polish**: 9 (T142-T150)
- **Validation**: 24 (T151-T174)

**MVP Scope**: US1 + US2 = 65 tasks (Setup + Foundational + US1 + US2)

**Parallel Opportunities**: 80+ tasks marked [P] can run in parallel within their phase

**Constitution Compliance**: Phase 10 validates all 9 principles before production deployment

**Next Steps**: Start with Phase 1 (Setup), then Phase 2 (Foundational), then US1+US2 for MVP
