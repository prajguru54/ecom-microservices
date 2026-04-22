#!/usr/bin/env sh
set -e

echo "Starting order-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying order-service migrations..."
  alembic upgrade head
fi

echo "Starting order-service application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${SERVICE_PORT:-8006}"
