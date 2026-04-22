#!/usr/bin/env bash
set -euo pipefail

# Bootstraps PostgreSQL initialization for first-time setup.
# Databases are created by infra/postgres/init/001-create-databases.sql
# when the postgres data volume is empty.
# Usually run before migration scripts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -f ".env" ]]; then
  echo "Missing .env file at repository root."
  echo "Copy .env.example to .env and update values before running."
  exit 1
fi

echo "Ensuring postgres is running..."
docker compose up -d postgres

echo "Databases are initialized automatically from infra/postgres/init/001-create-databases.sql"
echo "If this is not the first startup, recreate postgres volume to re-run init scripts:"
echo "  docker compose down -v postgres"
