# Quickstart Guide: Multi-Strategy Trading Platform

**Last Updated**: 2025-10-31  
**Target Audience**: Developers setting up local development environment

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Git**: 2.30 or higher

### Optional Tools

- **PostgreSQL Client**: psql or pgAdmin
- **Redis Client**: redis-cli
- **Kafka Tools**: kafkacat or Kafka UI

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd VELOX-final
git checkout 1-multi-strategy-platform
```

### 2. Start Infrastructure Services

```bash
cd infrastructure
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Kafka + Zookeeper (ports 9092, 2181)
- Kafka UI (port 8080)

### 3. Verify Services

```bash
# Check all services are running
docker-compose ps

# Expected output:
# NAME                STATUS    PORTS
# postgres            running   0.0.0.0:5432->5432/tcp
# redis               running   0.0.0.0:6379->6379/tcp
# kafka               running   0.0.0.0:9092->9092/tcp
# zookeeper           running   0.0.0.0:2181->2181/tcp
# kafka-ui            running   0.0.0.0:8080->8080/tcp
```

### 4. Initialize Database

```bash
# Run database migrations
cd ../services/dashboard-api-service
python -m alembic upgrade head
```

### 5. Start Backend Services

```bash
# Terminal 1: Market Data Service
cd services/market-data-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py

# Terminal 2: Strategy Engine Service
cd services/strategy-engine-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py

# Terminal 3: Dashboard API Service
cd services/dashboard-api-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### 6. Start Frontend

```bash
# Terminal 4: React Frontend
cd frontend
npm install
npm start
```

Frontend will open at `http://localhost:3000`

### 7. Create Admin User

```bash
# Use API endpoint or database seed script
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@velox.com",
    "password": "admin123",
    "full_name": "Admin User",
    "role": "ADMIN"
  }'
```

### 8. Login and Explore

1. Open `http://localhost:3000`
2. Login with `admin@velox.com` / `admin123`
3. Create your first strategy
4. Activate in paper trading mode
5. Monitor real-time dashboard

## Detailed Setup

### Environment Configuration

Create `.env` files for each service:

**services/dashboard-api-service/.env**:
```env
DATABASE_URL=postgresql://velox:velox123@localhost:5432/velox_trading
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
```

**services/market-data-service/.env**:
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379/0
SMARTAPI_API_KEY=your-smartapi-key
SMARTAPI_CLIENT_ID=your-client-id
SMARTAPI_PASSWORD=your-password
LOG_LEVEL=INFO
```

**services/strategy-engine-service/.env**:
```env
DATABASE_URL=postgresql://velox:velox123@localhost:5432/velox_trading
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379/0
STRATEGY_DIR=./src/strategies
LOG_LEVEL=INFO
```

**frontend/.env**:
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### Database Setup

#### Option 1: Automatic Migration (Recommended)

```bash
cd services/dashboard-api-service
python -m alembic upgrade head
```

#### Option 2: Manual SQL

```bash
psql -h localhost -U velox -d velox_trading -f infrastructure/postgres/init.sql
```

#### Seed Data (Optional)

```bash
python scripts/seed_data.py
```

This creates:
- Admin user
- Sample instruments (RELIANCE, TCS, INFY)
- Sample strategy configuration

### Kafka Topic Creation

Topics are auto-created by services, but you can pre-create them:

```bash
cd infrastructure/kafka
./topics.sh
```

Or manually:

```bash
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic market-data-stream \
  --partitions 10 \
  --replication-factor 1

docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic signal-events \
  --partitions 5 \
  --replication-factor 1

docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic order-events \
  --partitions 5 \
  --replication-factor 1
```

### Verify Setup

#### 1. Check Backend Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "services": {...}}
```

#### 2. Check Kafka Topics

```bash
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
# Expected: market-data-stream, signal-events, order-events, ...
```

#### 3. Check Redis Connection

```bash
redis-cli ping
# Expected: PONG
```

#### 4. Check PostgreSQL Connection

```bash
psql -h localhost -U velox -d velox_trading -c "SELECT COUNT(*) FROM users;"
# Expected: count (1 if seed data loaded)
```

## Development Workflow

### Running Tests

#### Backend Unit Tests

```bash
cd services/strategy-engine-service
pytest tests/unit/ -v --cov=src
```

#### Backend Integration Tests

```bash
cd services/strategy-engine-service
pytest tests/integration/ -v
```

#### Frontend Tests

```bash
cd frontend
npm test
```

#### End-to-End Tests

```bash
cd tests/e2e
npm run cypress:run
```

### Code Quality

#### Backend Linting

```bash
cd services/strategy-engine-service
black src/ tests/
flake8 src/ tests/
mypy src/
```

#### Frontend Linting

```bash
cd frontend
npm run lint
npm run format
```

### Hot Reload

All services support hot reload:

- **Backend**: FastAPI with `--reload` flag
- **Frontend**: React with `npm start`
- **Changes**: Edit code and see changes immediately

### Debugging

#### Backend Debugging (VS Code)

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Dashboard API Service",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/services/dashboard-api-service",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/services/dashboard-api-service"
      }
    }
  ]
}
```

#### Frontend Debugging (Chrome DevTools)

1. Open Chrome DevTools
2. Go to Sources tab
3. Set breakpoints in React components
4. Inspect WebSocket messages in Network tab

### Monitoring

#### Kafka UI

Open `http://localhost:8080` to view:
- Topics and messages
- Consumer groups
- Broker health

#### Redis Commander (Optional)

```bash
docker run -d --name redis-commander \
  -p 8081:8081 \
  -e REDIS_HOSTS=local:host.docker.internal:6379 \
  rediscommander/redis-commander
```

Open `http://localhost:8081`

#### PostgreSQL Admin (Optional)

```bash
docker run -d --name pgadmin \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@velox.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4
```

Open `http://localhost:5050`

## Common Issues

### Issue: Kafka Connection Refused

**Solution**: Ensure Kafka is running and accessible

```bash
docker-compose ps kafka
docker logs kafka
```

If Kafka is not starting, check Docker resources (increase memory to 4GB+)

### Issue: Database Migration Fails

**Solution**: Reset database

```bash
docker-compose down -v
docker-compose up -d postgres
sleep 5
python -m alembic upgrade head
```

### Issue: Frontend Cannot Connect to Backend

**Solution**: Check CORS configuration

Ensure `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`

### Issue: WebSocket Connection Fails

**Solution**: Check JWT token

Ensure access token is valid and not expired. Refresh token if needed.

### Issue: Market Data Not Streaming

**Solution**: Check SmartAPI credentials

Verify API key, client ID, and password in `.env` file. Test connection:

```bash
python scripts/test_smartapi_connection.py
```

## Production Deployment

### Docker Compose (Staging)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes (Production)

```bash
kubectl apply -f infrastructure/k8s/
```

See `infrastructure/k8s/README.md` for detailed Kubernetes setup.

## Next Steps

1. **Read Documentation**: Review `data-model.md` and API contracts
2. **Create Strategy**: Implement custom strategy in `services/strategy-engine-service/src/strategies/`
3. **Run Paper Trading**: Deploy strategy and monitor for 30 days
4. **Analyze Performance**: Use analytics dashboard to review metrics
5. **Go Live**: After validation, transition to live trading mode

## Support

- **Documentation**: See `specs/1-multi-strategy-platform/` directory
- **API Reference**: `http://localhost:8000/docs` (Swagger UI)
- **Kafka UI**: `http://localhost:8080`
- **Logs**: `docker-compose logs -f <service-name>`

## Architecture Overview

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Dashboard API  │
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ▼         ▼            ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐ ┌─────────┐
│ Market │ │Strategy│ │  Order   │ │Position │
│  Data  │ │ Engine │ │Management│ │Tracking │
└───┬────┘ └───┬───┘ └────┬─────┘ └────┬────┘
    │          │           │            │
    └──────────┴───────────┴────────────┘
               │
         ┌─────┴─────┬─────────┬────────┐
         ▼           ▼         ▼        ▼
    ┌────────┐  ┌────────┐ ┌──────┐ ┌──────┐
    │ Kafka  │  │ Redis  │ │Postgres│ │Broker│
    └────────┘  └────────┘ └──────┘ └──────┘
```

## Development Checklist

- [ ] Infrastructure services running (Docker Compose)
- [ ] Database migrated (Alembic)
- [ ] Backend services started (all 7 microservices)
- [ ] Frontend started (React)
- [ ] Admin user created
- [ ] Sample strategy deployed
- [ ] Paper trading active
- [ ] Dashboard showing real-time updates
- [ ] Tests passing (unit + integration)
- [ ] Code linted and formatted

**Ready to build! 🚀**
