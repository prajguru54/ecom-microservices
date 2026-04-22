#!/usr/bin/env sh
set -e

echo "Starting gateway-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying gateway-service migrations..."
  alembic upgrade head
fi

echo "Starting gateway-service application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8003}"
