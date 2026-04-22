#!/usr/bin/env sh
set -e

echo "Starting inventory-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying inventory-service migrations..."
  alembic upgrade head
fi

echo "Starting inventory-service application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${SERVICE_PORT:-8007}"
