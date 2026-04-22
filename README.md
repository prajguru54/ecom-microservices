# ecom-microservices

Beginner-friendly ecommerce microservices project for learning high-level system design concepts through a practical, runnable setup.

Concepts covered:

- API gateway and reverse proxy
- Load balancing
- Caching
- Message queue and pub/sub
- Service boundaries in a monorepo

For architecture and implementation details, see `AGENTS.md`.

## Run The App

### 1) Prerequisites

- Docker and Docker Compose
- Python `3.10+`
- Node.js `18+`

### 2) Configure environment

From the repository root:

```bash
cp .env.example .env
```

Update values in `.env` before startup.

### 3) Start infrastructure services

```bash
./scripts/dev-up.sh
```

This starts Postgres, Redis, RabbitMQ, Nginx, Prometheus, and Grafana.

### 4) Start backend services (one terminal per service)

```bash
cd services/gateway-service && source .venv/bin/activate && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
cd services/catalog-service && source .venv/bin/activate && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
cd services/cart-service && source .venv/bin/activate && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
cd services/order-service && source .venv/bin/activate && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8006
cd services/inventory-service && source .venv/bin/activate && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8007
cd services/notification-service && source .venv/bin/activate && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8008
```

### 5) Start frontend

```bash
cd frontend && npm install
cd frontend && npm run dev
```

Open the URL printed by Vite (usually `http://localhost:5173`).

### 6) Stop everything

```bash
./scripts/dev-down.sh
```
