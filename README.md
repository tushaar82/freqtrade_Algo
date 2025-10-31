# VELOX Multi-Strategy Trading Platform

A microservices-based algorithmic trading platform for deploying and managing multiple trading strategies simultaneously with real-time monitoring, paper trading validation, and multi-broker support.

## Features

- **Multi-Strategy Execution**: Deploy 100+ concurrent strategies across 500+ instruments
- **Real-Time Dashboard**: Live P&L charts, position tracking, price vs stop-loss visualization
- **Paper Trading**: 30-day validation period before live deployment
- **Multi-Broker Support**: Broker adapter pattern (SmartAPI, Zerodha Kite)
- **Risk Management**: Pre-trade checks, kill switches, loss limits (Rs. 5000/- daily)
- **Plug-and-Play Strategies**: Dynamic strategy loading without system restart
- **Role-Based Access**: Admin (full access) and Investor (read-only dashboard)

## Architecture

**Microservices**:
- Market Data Service (Kafka producer)
- Strategy Engine Service (signal generation)
- Order Management Service (order lifecycle, broker adapter)
- Risk Management Service (pre-trade checks, loss limits)
- Position Tracking Service (position calculation, stop-loss)
- Analytics Service (P&L, performance metrics)
- Dashboard API Service (REST API + WebSocket)
- Alert Service (email/SMS/Telegram)

**Tech Stack**:
- Backend: Python 3.11+, FastAPI 0.104+
- Frontend: React 18+, TypeScript, TailwindCSS
- Message Broker: Apache Kafka 3.5+
- Cache: Redis 7+
- Database: PostgreSQL 15+
- Infrastructure: Docker, Docker Compose

## Quick Start

See [specs/1-multi-strategy-platform/quickstart.md](specs/1-multi-strategy-platform/quickstart.md) for detailed setup instructions.

### 5-Minute Setup

```bash
# 1. Start infrastructure
cd infrastructure
docker-compose up -d

# 2. Verify services
docker-compose ps

# 3. Create Kafka topics
bash kafka/topics.sh

# 4. Initialize database
cd ../services/dashboard-api-service
python -m alembic upgrade head

# 5. Start services (see quickstart.md for details)
```

## Documentation

- **Specification**: [specs/1-multi-strategy-platform/spec.md](specs/1-multi-strategy-platform/spec.md)
- **Implementation Plan**: [specs/1-multi-strategy-platform/plan.md](specs/1-multi-strategy-platform/plan.md)
- **Tasks**: [specs/1-multi-strategy-platform/tasks.md](specs/1-multi-strategy-platform/tasks.md)
- **Data Model**: [specs/1-multi-strategy-platform/data-model.md](specs/1-multi-strategy-platform/data-model.md)
- **API Contracts**: [specs/1-multi-strategy-platform/contracts/](specs/1-multi-strategy-platform/contracts/)

## Constitution Compliance

This platform adheres to the [VELOX Constitution](.specify/memory/constitution.md) with 9 core principles:
1. Regulatory Compliance & Risk Management
2. System Architecture & Reliability
3. Market Data & Order Management
4. Multi-Broker Architecture
5. Strategy Development & Backtesting
6. Monitoring & Alerting
7. Capital Preservation Over Profit Maximization
8. Code Quality & Testing
9. Performance Metrics & Analysis

## Development Status

**Current Phase**: Implementation Phase 1 (Setup)  
**Branch**: `1-multi-strategy-platform`  
**Progress**: 6/174 tasks complete

## License

Proprietary - VELOX Trading System
