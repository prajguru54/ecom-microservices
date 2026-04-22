#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -f ".env" ]]; then
  echo "Missing .env file at repository root."
  echo "Copy .env.example to .env and update values before running."
  exit 1
fi

echo "Starting infra services (postgres, redis, rabbitmq, nginx, prometheus, grafana)..."
docker compose up -d postgres redis rabbitmq nginx prometheus grafana

echo "Infra is starting. Use 'docker compose ps' to verify health."
