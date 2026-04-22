#!/usr/bin/env sh
set -e

echo "Starting auth-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying auth-service migrations..."
  alembic upgrade head
fi

echo "Starting auth-service application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${SERVICE_PORT:-8001}"
