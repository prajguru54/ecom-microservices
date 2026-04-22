# AGENTS.md

Detailed technical reference for this repository lives here.

## Architecture Overview

This project follows a **monorepo** setup (all services and UI in one repository) while keeping each service independently buildable and deployable.

### Core services

- `gateway-service` (reverse proxy/API gateway entrypoint)
- `catalog-service` (products, categories, product details)
- `cart-service` (user cart operations)
- `order-service` (place orders, order lifecycle)
- `inventory-service` (stock reserve/reduce and stock events)
- `notification-service` (async email/SMS/mock notifications)
- `ui/web` (customer-facing frontend)

### Infrastructure components

- `nginx` for reverse proxy + load balancing
- `redis` for caching and simple pub/sub
- `rabbitmq` for queue-based async workflows
- `postgres` (or sqlite for local experiments) for service data

### Observability (start simple)

Start with only these two tools:

- `prometheus` for service and infrastructure metrics collection
- `grafana` for dashboards and basic alerts

Add OpenTelemetry tracing only after the core flows are stable.

## How HLD Concepts Map Here

- **DNS**: subdomains like `shop.local`, `api.local`, `media.local`
- **Reverse Proxy**: Nginx routes requests to relevant services
- **Load Balancer**: multiple instances of hot services (for example catalog/order) behind Nginx
- **Caching**: Redis caches frequent reads (products, carts)
- **CDN**: static assets and product media served through CDN or CDN-like static domain
- **Message Queue**: order placed -> queued jobs (payment simulation, inventory update, notifications)
- **Pub/Sub**: order and inventory events are published for interested consumers

## Deployment Plan

### Phase 1: Local single-node (recommended starting point)

- Run everything using Docker Compose
- Start with one instance per service
- Validate APIs, queue flow, and event flow end-to-end
- Run only basic observability: Prometheus + Grafana
- For API-only local development, you can also run services directly with `uvicorn` (without Docker)

### Phase 2: Scale selected services

- Increase replicas for high-traffic services (`catalog-service`, `order-service`)
- Keep other services single-replica initially
- Confirm load balancing behavior through gateway/reverse proxy
- Add OpenTelemetry Collector and distributed tracing (optional at this phase)

### Phase 3 (optional): Kubernetes

- Separate Deployment per service
- Independent scaling and rolling deployments

## Run Locally Without Docker

Use this mode when you want quick iteration on service code.
You will still need infra dependencies (Redis, RabbitMQ, Postgres) running separately.

### Service Port Assignment

- `gateway-service`: `8003`
- `catalog-service`: `8004`
- `cart-service`: `8005`
- `order-service`: `8006`
- `inventory-service`: `8007`
- `notification-service`: `8008`

### Run Frontend (`frontend/`)

Use this to start the customer-facing UI locally.

#### Prerequisites

- Node.js `18+` (or latest LTS)
- `npm` (project includes `frontend/package-lock.json`)

#### Install dependencies

From repo root:

```bash
cd frontend && npm install
```

#### Start dev server

```bash
cd frontend && npm run dev
```

Then open the local URL shown by Vite (usually `http://localhost:5173`).

#### Build for production

```bash
cd frontend && npm run build
```

#### Preview production build locally

```bash
cd frontend && npm run preview
```

#### Optional quality checks

```bash
cd frontend && npm run lint
cd frontend && npm run format
```

### Prerequisites

1. Start infra dependencies externally (or via partial compose):
   - Redis
   - RabbitMQ
   - Postgres
2. In each service, copy `.env.example` to `.env` and set connection values.
3. Install dependencies for each service from its own `pyproject.toml`.

### Copy-Paste Commands (one terminal per service)

Run these from repo root `ecom-microservices/`:

#### gateway-service (port 8003)

```bash
cd services/gateway-service && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

#### catalog-service (port 8004)

```bash
cd services/catalog-service && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

#### cart-service (port 8005)

```bash
cd services/cart-service && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```

#### order-service (port 8006)

```bash
cd services/order-service && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8006
```

#### inventory-service (port 8007)

```bash
cd services/inventory-service && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8007
```

#### notification-service (port 8008)

```bash
cd services/notification-service && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8008
```

## Deploying Prometheus and Grafana

Use this as the default way to run observability in Phase 1.

### Option A: Docker Compose (recommended)

1. Ensure these paths exist in repo:
   - `infra/monitoring/prometheus.yml`
   - `infra/monitoring/grafana/provisioning/`
2. Add these services to `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./infra/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    volumes:
      - grafana-data:/var/lib/grafana
      - ./infra/monitoring/grafana/provisioning:/etc/grafana/provisioning:ro

volumes:
  prometheus-data:
  grafana-data:
```

3. Start observability:
   - `docker compose up -d prometheus grafana`
4. Verify:
   - Prometheus UI: `http://localhost:9090`
   - Grafana UI: `http://localhost:3000`
5. In Grafana, add Prometheus datasource (if not auto-provisioned):
   - URL: `http://prometheus:9090`

### Option B: Kubernetes (later, Phase 3)

Deploy with Helm after the core system is stable:

1. Create namespace:
   - `kubectl create namespace monitoring`
2. Install Prometheus:
   - `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`
   - `helm repo update`
   - `helm install prom prometheus-community/prometheus -n monitoring`
3. Install Grafana:
   - `helm repo add grafana https://grafana.github.io/helm-charts`
   - `helm repo update`
   - `helm install grafana grafana/grafana -n monitoring`
4. Expose locally for verification:
   - `kubectl get svc -n monitoring`
   - Port-forward the Prometheus and Grafana services shown above to local ports `9090` and `3000`

## What "Single Instance First" Means

Begin with **exactly one running instance per service** to reduce complexity and make debugging easier.
Once behavior is stable, scale only services that need throughput or high availability.

## What "Add Redis Cache for Product and Cart Reads" Means

Use cache-aside reads for frequent requests:

1. Check Redis first (`product:{id}`, `cart:{user_id}`)
2. On cache miss, read from DB
3. Store response in Redis (usually with TTL)
4. Return result

When product/cart data changes, invalidate or refresh related cache keys.

## Independent Redeploy in Monorepo

Monorepo does **not** block independent deployments.

You can redeploy one service without touching others by:

- Keeping separate Dockerfile/image per service
- Running service-specific CI jobs using path filters
- Updating only the changed service runtime

### Example (Docker Compose)

- Rebuild one service:
    - `docker compose build cart-service`
- Recreate only that service:
    - `docker compose up -d --no-deps cart-service`

### Example (Kubernetes)

- Build/push new image only for one service
- Update only that deployment image
- Kubernetes performs rolling update for that service alone

## Suggested Folder Structure (FastAPI-style, UI deferred as `frontend`)

```text
ecom-microservices/
├── README.md
├── AGENTS.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── api-contracts.md
│   ├── event-flows.md
│   └── deployment.md
├── infra/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── conf.d/
│   │       └── default.conf
│   ├── redis/
│   │   └── redis.conf
│   ├── rabbitmq/
│   │   └── definitions.json
│   ├── postgres/
│   │   └── init/
│   │       ├── 001-create-databases.sql
│   │       └── 002-seed-minimal.sql
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana/
│           └── provisioning/
├── services/
│   ├── gateway-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── dependencies.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   └── proxy.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   └── config.py
│   │   │   └── schemas/
│   │   │       └── __init__.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── .env.example
│   ├── catalog-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── dependencies.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   ├── products.py
│   │   │   │   └── categories.py
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── repositories/
│   │   │   │   └── __init__.py
│   │   │   ├── schemas/
│   │   │   │   └── __init__.py
│   │   │   └── core/
│   │   │       ├── __init__.py
│   │   │       └── config.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── .env.example
│   ├── cart-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── dependencies.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   └── carts.py
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── repositories/
│   │   │   │   └── __init__.py
│   │   │   └── schemas/
│   │   │       └── __init__.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── .env.example
│   ├── order-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── dependencies.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   └── orders.py
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── repositories/
│   │   │   │   └── __init__.py
│   │   │   ├── schemas/
│   │   │   │   └── __init__.py
│   │   │   └── publishers/
│   │   │       └── __init__.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── .env.example
│   ├── inventory-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── dependencies.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   └── inventory.py
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── repositories/
│   │   │   │   └── __init__.py
│   │   │   ├── schemas/
│   │   │   │   └── __init__.py
│   │   │   └── subscribers/
│   │   │       └── __init__.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── .env.example
│   └── notification-service/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── dependencies.py
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   └── health.py
│       │   ├── consumers/
│       │   │   └── __init__.py
│       │   └── templates/
│       ├── tests/
│       ├── Dockerfile
│       ├── pyproject.toml
│       ├── uv.lock
│       └── .env.example
├── frontend/
│   └── (to be decided later)
├── shared/
│   ├── contracts/
│   │   ├── events/
│   │   │   ├── order-created.json
│   │   │   ├── stock-reserved.json
│   │   │   └── order-status-updated.json
│   └── scripts/
│       ├── wait-for-it.sh
│       └── seed-data.py
└── scripts/
    ├── dev-up.sh
    ├── dev-down.sh
    ├── test-all.sh
    ├── lint-all.sh
    └── smoke-test.sh
```
