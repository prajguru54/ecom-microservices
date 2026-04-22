#!/usr/bin/env bash
set -euo pipefail

# Starts Docker Compose services for local development.
# - No args: starts every service in docker-compose.yml
# - With args: starts only the given services
# Pairs with scripts/dev-down.sh to stop the stack.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -f ".env" ]]; then
  echo "Missing .env file at repository root."
  echo "Copy .env.example to .env and update values before running."
  exit 1
fi

# Examples:
#   ./scripts/dev-up.sh
#   ./scripts/dev-up.sh postgres redis
#   ./scripts/dev-up.sh postgres pgadmin
if [[ $# -gt 0 ]]; then
  echo "Starting selected services: $*"
  docker compose up -d --build "$@"
else
  echo "Starting all services defined in docker-compose.yml..."
  docker compose up -d --build
fi

echo "Infra is starting. Use 'docker compose ps' to verify health."
