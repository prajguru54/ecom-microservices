# Auth Service

JWT-based authentication microservice for the ecom-microservices project.

## Features

- User registration and login
- JWT token generation and validation
- Password hashing with bcrypt
- PostgreSQL database with Alembic migrations
- FastAPI with automatic API documentation
- Prometheus metrics instrumentation
- Comprehensive test suite

## API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /health/db` - Database connectivity check

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login (returns JWT token)
- `POST /auth/validate` - Validate JWT token
- `GET /auth/me` - Get current user info (requires authentication)

## Development Setup

1. **Setup environment:**
   ```bash
   ./setup-dev.sh
   source .venv/bin/activate
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the service:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

5. **Run tests:**
   ```bash
   pytest
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Environment Variables

See `.env.example` for required configuration variables:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `JWT_ALGORITHM` - Algorithm for JWT signing (default: HS256)
- `SERVICE_PORT` - Port to run the service on (default: 8001)

## Docker Usage

```bash
docker build -t auth-service .
docker run -p 8001:8001 --env-file .env auth-service
```