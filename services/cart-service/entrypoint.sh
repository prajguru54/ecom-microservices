#!/usr/bin/env sh
set -e

echo "Starting cart-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying cart-service migrations..."
  alembic upgrade head
fi

echo "Starting cart-service application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${SERVICE_PORT:-8005}"
