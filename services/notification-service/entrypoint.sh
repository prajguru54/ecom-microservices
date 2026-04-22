#!/usr/bin/env sh
set -e

echo "Starting notification-service container..."

if [ -f "alembic.ini" ]; then
  echo "Applying notification-service migrations..."
  alembic upgrade head
fi

echo "Starting notification-service application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${SERVICE_PORT:-8008}"
