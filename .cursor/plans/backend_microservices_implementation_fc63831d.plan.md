---
name: Backend Microservices Implementation
overview: Build complete backend microservices architecture from scratch with JWT auth, separate databases per service, async messaging, caching, and observability - focused on getting a working demo quickly then iterating on architecture.
todos:
    - id: setup-infrastructure
      content: Create Docker Compose setup with PostgreSQL (multi-db), Redis, RabbitMQ, Nginx, Prometheus, Grafana
      status: pending
    - id: create-repo-structure
      content: Set up monorepo folder structure with services/, infra/, shared/, scripts/ directories
      status: pending
    - id: setup-alembic-migrations
      content: Configure Alembic for each service with separate database connections and migration environments
      status: pending
    - id: implement-auth-service
      content: Build JWT-based auth service with user registration/login, token validation
      status: pending
    - id: implement-gateway-service
      content: Create API gateway with request routing, auth middleware, rate limiting
      status: pending
    - id: implement-catalog-service
      content: Build product catalog service with Redis caching and database operations
      status: pending
    - id: implement-cart-service
      content: Create cart service with Redis-backed sessions and database persistence
      status: pending
    - id: implement-order-service
      content: Build order service with CRUD operations and RabbitMQ event publishing
      status: pending
    - id: implement-inventory-service
      content: Create inventory service with stock management and event consumption
      status: pending
    - id: implement-notification-service
      content: Build notification service as RabbitMQ consumer with email templates
      status: pending
    - id: setup-observability
      content: Configure Prometheus metrics collection and Grafana dashboards
      status: pending
    - id: add-service-tests
      content: Implement unit and integration tests for each service
      status: pending
    - id: create-dev-tooling
      content: Add development scripts for starting/stopping services and running tests
      status: pending
isProject: false
---

# Backend Microservices Implementation Plan

## Architecture Overview

```mermaid
graph TB
    subgraph external [External]
        Frontend[React Frontend]
        Users[Users]
    end

    subgraph gateway [Gateway Layer]
        Nginx[Nginx Load Balancer]
        Gateway[Gateway Service:8003]
    end

    subgraph services [Microservices]
        Auth[Auth Service:8001]
        Catalog[Catalog Service:8004]
        Cart[Cart Service:8005]
        Order[Order Service:8006]
        Inventory[Inventory Service:8007]
        Notification[Notification Service:8008]
    end

    subgraph infrastructure [Infrastructure]
        PgMain[(PostgreSQL)]
        Redis[(Redis Cache)]
        RabbitMQ[RabbitMQ]
        Prometheus[Prometheus]
        Grafana[Grafana]
    end

    subgraph databases [Separate Databases]
        AuthDB[(auth_db)]
        CatalogDB[(catalog_db)]
        CartDB[(cart_db)]
        OrderDB[(order_db)]
        InventoryDB[(inventory_db)]
    end

    Users --> Frontend
    Frontend --> Nginx
    Nginx --> Gateway

    Gateway --> Auth
    Gateway --> Catalog
    Gateway --> Cart
    Gateway --> Order
    Gateway --> Inventory

    Auth --> AuthDB
    Catalog --> CatalogDB
    Cart --> CartDB
    Order --> OrderDB
    Inventory --> InventoryDB

    PgMain --> AuthDB
    PgMain --> CatalogDB
    PgMain --> CartDB
    PgMain --> OrderDB
    PgMain --> InventoryDB

    Order --> RabbitMQ
    RabbitMQ --> Inventory
    RabbitMQ --> Notification

    Catalog --> Redis
    Cart --> Redis

    services --> Prometheus
    Prometheus --> Grafana
```

## Service Responsibilities

- **Auth Service (8001)**: JWT-based user registration/login, token validation
- **Gateway Service (8003)**: Request routing, auth middleware, rate limiting
- **Catalog Service (8004)**: Product/category management, search, caching
- **Cart Service (8005)**: Cart CRUD operations, Redis-backed sessions
- **Order Service (8006)**: Order creation, status management, event publishing
- **Inventory Service (8007)**: Stock management, reservation handling
- **Notification Service (8008)**: Email/SMS notifications via message consumption

## Implementation Phases

### Phase 1: Foundation Setup (Infrastructure & Contracts)

**Priority**: Critical foundation

**Deliverables**:

- Repository structure creation
- Docker Compose infrastructure setup
- Database initialization scripts
- Shared contracts and schemas
- Development tooling

**Key Files to Create**:

- [`docker-compose.yml`](docker-compose.yml) - Full infrastructure stack
- [`infra/postgres/init/001-create-databases.sql`](infra/postgres/init/001-create-databases.sql) - Database creation
- [`shared/contracts/events/`](shared/contracts/events/) - Event schemas
- [`scripts/dev-up.sh`](scripts/dev-up.sh), [`scripts/dev-down.sh`](scripts/dev-down.sh) - Development helpers
- [`scripts/init-databases.sh`](scripts/init-databases.sh) - Create all service databases
- [`scripts/migrate-all.sh`](scripts/migrate-all.sh) - Run migrations for all services
- [`scripts/migrate-service.sh`](scripts/migrate-service.sh) - Run migration for specific service
- [`.env.example`](.env.example) - Environment template

**Infrastructure Components**:

- PostgreSQL with separate databases (auth_db, catalog_db, cart_db, order_db, inventory_db)
- Redis for caching and sessions
- RabbitMQ for async messaging
- Nginx for load balancing
- Prometheus + Grafana for monitoring

### Phase 2: Auth Service (First Service)

**Priority**: Critical - needed by all other services

**Deliverables**:

- Complete JWT-based authentication service
- User registration and login endpoints
- Token validation middleware
- Database models and migrations

**Key Files to Create**:

- [`services/auth-service/app/main.py`](services/auth-service/app/main.py) - FastAPI app
- [`services/auth-service/app/models/user.py`](services/auth-service/app/models/user.py) - User model
- [`services/auth-service/app/routers/auth.py`](services/auth-service/app/routers/auth.py) - Auth endpoints
- [`services/auth-service/app/core/security.py`](services/auth-service/app/core/security.py) - JWT utilities
- [`services/auth-service/app/database.py`](services/auth-service/app/database.py) - Database session and engine
- [`services/auth-service/alembic.ini`](services/auth-service/alembic.ini) - Alembic configuration
- [`services/auth-service/migrations/env.py`](services/auth-service/migrations/env.py) - Alembic environment setup
- [`services/auth-service/migrations/versions/`](services/auth-service/migrations/versions/) - Migration files
- [`services/auth-service/pyproject.toml`](services/auth-service/pyproject.toml) - Dependencies

**API Endpoints**:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT)
- `POST /auth/validate` - Token validation (for other services)
- `GET /auth/me` - Get current user info

### Phase 3: Gateway Service (Request Router)

**Priority**: Critical - entry point for all requests

**Deliverables**:

- API Gateway with request routing
- Auth middleware integration
- Rate limiting and request/response logging
- Health check aggregation

**Key Files to Create**:

- [`services/gateway-service/app/main.py`](services/gateway-service/app/main.py) - FastAPI gateway app
- [`services/gateway-service/app/middleware/auth.py`](services/gateway-service/app/middleware/auth.py) - JWT validation middleware
- [`services/gateway-service/app/routers/proxy.py`](services/gateway-service/app/routers/proxy.py) - Service routing
- [`services/gateway-service/app/core/service_registry.py`](services/gateway-service/app/core/service_registry.py) - Service discovery

**Features**:

- Route `/auth/*` to Auth Service
- Route `/api/products/*` to Catalog Service
- Route `/api/cart/*` to Cart Service
- Route `/api/orders/*` to Order Service
- Route `/api/inventory/*` to Inventory Service

### Phase 4: Core Business Services (Synchronous APIs)

**Priority**: High - core functionality

**Deliverables**:

- Catalog Service with product management
- Cart Service with Redis backing
- Order Service with basic CRUD
- Inventory Service with stock management

**Catalog Service** ([`services/catalog-service/`](services/catalog-service/)):

- Product CRUD operations
- Category management
- Product search and filtering
- Redis caching for hot products
- Database: catalog_db (products, categories tables)
- Alembic migrations for schema management

**Key Migration Files**:

- [`services/catalog-service/alembic.ini`](services/catalog-service/alembic.ini)
- [`services/catalog-service/migrations/env.py`](services/catalog-service/migrations/env.py)
- [`services/catalog-service/migrations/versions/001_create_categories.py`](services/catalog-service/migrations/versions/001_create_categories.py)
- [`services/catalog-service/migrations/versions/002_create_products.py`](services/catalog-service/migrations/versions/002_create_products.py)

**Cart Service** ([`services/cart-service/`](services/cart-service/)):

- Cart CRUD operations
- Redis-backed cart sessions
- Cart item management
- Database: cart_db (for persistent cart history)
- Alembic migrations for cart persistence

**Order Service** ([`services/order-service/`](services/order-service/)):

- Order creation and status management
- Order history and tracking
- Integration point for payment simulation
- Database: order_db (orders, order_items tables)
- Alembic migrations for order management

**Inventory Service** ([`services/inventory-service/`](services/inventory-service/)):

- Stock level management
- Stock reservation/release operations
- Low stock alerts
- Database: inventory_db (inventory, reservations tables)
- Alembic migrations for inventory tracking

### Phase 5: Async Messaging & Event Flow

**Priority**: High - enables decoupled architecture

**Deliverables**:

- RabbitMQ event publishing from Order Service
- Event consumers in Inventory and Notification services
- Reliable message handling with retries
- Event schemas and contracts

**Key Events**:

- `order.created` - Published when order is placed
- `inventory.reserved` - Published when stock is reserved
- `inventory.insufficient` - Published when stock unavailable
- `order.confirmed` - Published when order is fully processed
- `notification.email.requested` - Published for email notifications

**Event Flow**:

```mermaid
sequenceDiagram
    participant User
    participant Order
    participant Inventory
    participant Notification
    participant RabbitMQ

    User->>Order: POST /orders
    Order->>RabbitMQ: publish order.created
    Order->>User: 201 Order Created

    RabbitMQ->>Inventory: consume order.created
    Inventory->>RabbitMQ: publish inventory.reserved

    RabbitMQ->>Order: consume inventory.reserved
    Order->>RabbitMQ: publish order.confirmed

    RabbitMQ->>Notification: consume order.confirmed
    Notification->>Notification: send email
```

### Phase 6: Caching Layer (Redis Integration)

**Priority**: Medium - performance optimization

**Deliverables**:

- Redis cache-aside pattern implementation
- Cache invalidation strategies
- Cache hit/miss metrics
- TTL management

**Caching Strategy**:

- **Catalog Service**: Cache product details, category lists
- **Cart Service**: Cache active cart sessions
- **Auth Service**: Cache user sessions and token blacklists

### Phase 7: Notification Service (Async Consumer)

**Priority**: Medium - completes the async flow

**Deliverables**:

- Email notification service (mock SMTP initially)
- RabbitMQ message consumers
- Notification templates
- Delivery status tracking

**Key Files to Create**:

- [`services/notification-service/app/consumers/order_consumer.py`](services/notification-service/app/consumers/order_consumer.py)
- [`services/notification-service/app/services/email_service.py`](services/notification-service/app/services/email_service.py)
- [`services/notification-service/app/templates/`](services/notification-service/app/templates/) - Email templates

### Phase 8: Observability & Monitoring

**Priority**: Medium - operational visibility

**Deliverables**:

- Prometheus metrics in all services
- Grafana dashboards
- Application logging with correlation IDs
- Health checks and alerting

**Key Metrics**:

- Request latency and error rates per service
- Database connection pool usage
- Redis cache hit rates
- RabbitMQ queue depths
- Order processing funnel metrics

**Key Files to Create**:

- [`infra/monitoring/prometheus.yml`](infra/monitoring/prometheus.yml)
- [`infra/monitoring/grafana/dashboards/`](infra/monitoring/grafana/dashboards/)
- [`infra/monitoring/grafana/provisioning/`](infra/monitoring/grafana/provisioning/)

### Phase 9: Testing Framework

**Priority**: Medium - service-level testing

**Deliverables**:

- Unit tests for each service
- Service-level integration tests
- Test fixtures and factories
- CI/CD test automation

**Testing Strategy**:

- **Unit Tests**: Repository layer, business logic, utilities
- **Integration Tests**: API endpoints with test database
- **Contract Tests**: Event schema validation
- **Smoke Tests**: Basic end-to-end health checks

### Phase 10: Production Hardening

**Priority**: Low - post-demo improvements

**Deliverables**:

- Error handling and retry policies
- Input validation and security headers
- Database transaction management
- Graceful shutdown handling
- Performance optimization

## Database Schema Design

### auth_db

- **users**: id, username, email, password_hash, created_at, updated_at, is_active

### catalog_db

- **categories**: id, name, description, parent_id, created_at
- **products**: id, name, description, price, category_id, created_at, updated_at, is_active

### cart_db

- **carts**: id, user_id, created_at, updated_at
- **cart_items**: id, cart_id, product_id, quantity, added_at

### order_db

- **orders**: id, user_id, status, total_amount, created_at, updated_at
- **order_items**: id, order_id, product_id, quantity, unit_price

### inventory_db

- **inventory**: id, product_id, available_quantity, reserved_quantity, updated_at
- **reservations**: id, product_id, order_id, quantity, expires_at, status

## Alembic Migration Strategy

### Per-Service Migration Setup

Each service that uses a database will have its own Alembic configuration:

**Service Structure with Alembic**:

```
services/{service-name}/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── database.py      # Database session/engine
│   └── ...
├── alembic.ini          # Alembic config file
├── migrations/
│   ├── env.py          # Alembic environment
│   ├── script.py.mako  # Migration template
│   └── versions/       # Generated migration files
├── pyproject.toml       # Include alembic dependency
└── .env.example        # Database URL template
```

**Key Alembic Files per Service**:

- **alembic.ini**: Configuration pointing to service-specific database
- **migrations/env.py**: Environment setup with service models import
- **migrations/versions/**: Auto-generated migration files

**Migration Commands per Service**:

```bash
# Initialize Alembic (one-time setup)
cd services/{service-name}
source .venv/bin/activate
alembic init migrations

# Generate migration after model changes
alembic revision --autogenerate -m "create users table"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Database Connection Strategy

Each service connects to its own database using environment variables:

**Auth Service**: `DATABASE_URL=postgresql://user:pass@localhost:5432/auth_db`
**Catalog Service**: `DATABASE_URL=postgresql://user:pass@localhost:5432/catalog_db`
**Cart Service**: `DATABASE_URL=postgresql://user:pass@localhost:5432/cart_db`
**Order Service**: `DATABASE_URL=postgresql://user:pass@localhost:5432/order_db`
**Inventory Service**: `DATABASE_URL=postgresql://user:pass@localhost:5432/inventory_db`

### Migration Workflow

1. **Development**: Run migrations locally after model changes
2. **Testing**: Use separate test databases with fresh migrations
3. **Production**: Include migration step in deployment scripts

**Development Scripts**:

```bash
# Run all service migrations
./scripts/migrate-all.sh

# Run specific service migration
./scripts/migrate-service.sh auth-service
```

## Development Environment Setup

1. **Prerequisites**: Docker, Docker Compose, Python 3.10+, uv package manager
2. **Infrastructure**: Start PostgreSQL, Redis, RabbitMQ with `docker compose up -d postgres redis rabbitmq`
3. **Service Development**: Each service has individual `.venv` with `uv sync`
4. **Database Setup**: Run `./scripts/init-databases.sh` to create all databases
5. **Migrations**: Run `./scripts/migrate-all.sh` to apply all service migrations
6. **Local Development**: Use `scripts/dev-up.sh` to start all services
7. **Testing**: `pytest` per service with separate test databases

## Service Communication Patterns

- **Synchronous**: Gateway → Services (HTTP/REST)
- **Asynchronous**: Order → Inventory → Notification (RabbitMQ events)
- **Caching**: Catalog/Cart → Redis (cache-aside pattern)
- **Authentication**: JWT tokens validated at gateway and passed to services

## Port Assignments

- Gateway Service: 8003
- Auth Service: 8001
- Catalog Service: 8004
- Cart Service: 8005
- Order Service: 8006
- Inventory Service: 8007
- Notification Service: 8008
- PostgreSQL: 5432
- Redis: 6379
- RabbitMQ: 5672 (AMQP), 15672 (Management UI)
- Nginx: 80
- Prometheus: 9090
- Grafana: 3000
