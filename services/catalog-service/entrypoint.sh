#!/usr/bin/env sh
set -e

echo "Starting catalog-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying catalog-service migrations..."
  uv run alembic upgrade head
fi

echo "Starting catalog-service application..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${SERVICE_PORT:-8004}"
