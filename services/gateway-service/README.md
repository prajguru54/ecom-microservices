# Gateway Service

API Gateway for E-commerce Microservices that provides request routing, authentication, rate limiting, and service aggregation.

## Features

- **Request Routing**: Routes requests to appropriate backend services
- **JWT Authentication**: Validates JWT tokens and passes user context to services
- **Rate Limiting**: Redis-based sliding window rate limiting
- **Service Discovery**: Configurable service registry with health checking
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: Aggregated health status from all backend services
- **Error Handling**: Proper error responses and service unavailability handling

## Architecture

The Gateway Service acts as the single entry point for all client requests and routes them to the appropriate backend services:

```
Client Request → Gateway → Auth/Catalog/Cart/Order/Inventory Services
```

### Service Routing

- `/auth/*` → Auth Service (8001)
- `/api/products/*` → Catalog Service (8004)  
- `/api/cart/*` → Cart Service (8005)
- `/api/orders/*` → Order Service (8006)
- `/api/inventory/*` → Inventory Service (8007)

## Installation

1. Navigate to the service directory:
```bash
cd services/gateway-service
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Copy environment configuration:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration.

## Configuration

### Required Environment Variables

```bash
# Security
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Backend Services
AUTH_SERVICE_URL=http://localhost:8001
CATALOG_SERVICE_URL=http://localhost:8004
CART_SERVICE_URL=http://localhost:8005
ORDER_SERVICE_URL=http://localhost:8006
INVENTORY_SERVICE_URL=http://localhost:8007

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Optional Configuration

```bash
# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
DEBUG=false
PORT=8003
LOG_LEVEL=INFO
```

## Usage

### Development Mode

```bash
cd services/gateway-service
source .venv/bin/activate
uvicorn app.main:app --reload --port 8003
```

### Production Mode

```bash
cd services/gateway-service
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

### Docker

```bash
# Build image
docker build -t gateway-service .

# Run container
docker run -p 8003:8003 --env-file .env gateway-service
```

## API Endpoints

### Health Checks

- `GET /health/` - Basic gateway health check
- `GET /health/services` - Health status of all backend services  
- `GET /health/ready` - Readiness check (gateway ready when auth service is healthy)

### Documentation

- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## Authentication

The gateway validates JWT tokens for protected routes and passes user information to backend services via headers:

- `X-User-ID`: User ID from token
- `X-Username`: Username from token  
- `X-User-Email`: User email from token

### Public Routes (No Authentication Required)

- `/auth/login`
- `/auth/register`
- `GET /api/products/*` (product browsing)
- `/health/*`
- `/docs`

## Rate Limiting

The gateway implements sliding window rate limiting using Redis:

- Default: 100 requests per 60 seconds per client
- Client identification: User ID (if authenticated) or IP address
- Rate limit headers included in responses

## Error Handling

The gateway provides proper error responses for various scenarios:

- `401 Unauthorized` - Missing or invalid JWT token
- `429 Too Many Requests` - Rate limit exceeded
- `502 Bad Gateway` - Internal proxy error
- `503 Service Unavailable` - Backend service not reachable
- `504 Gateway Timeout` - Backend service timeout

## Testing

Run tests with pytest:

```bash
cd services/gateway-service
source .venv/bin/activate
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Monitoring

The gateway exposes metrics and logging for observability:

- Structured logging with correlation IDs
- Request/response logging
- Service health monitoring
- Rate limiting metrics

## Development

### Project Structure

```
services/gateway-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── dependencies.py      # Dependency injection
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── service_registry.py  # Service discovery
│   ├── middleware/
│   │   ├── auth.py          # JWT authentication
│   │   └── rate_limit.py    # Rate limiting
│   ├── routers/
│   │   ├── health.py        # Health check endpoints
│   │   └── proxy.py         # Service routing
│   └── schemas/
├── tests/                   # Test files
├── Dockerfile              # Docker configuration
├── pyproject.toml          # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

### Adding New Routes

To add routing for a new service:

1. Update `SERVICE_ROUTES` in `app/core/config.py`
2. Add the service URL to settings and environment variables
3. The proxy will automatically handle routing

### Middleware Order

Middleware is applied in this order:
1. CORS
2. Rate Limiting  
3. Authentication
4. Request Processing