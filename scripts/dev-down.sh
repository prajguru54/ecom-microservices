#!/usr/bin/env bash
set -euo pipefail

# Stops all Docker Compose services started by scripts/dev-up.sh.
# Use this to cleanly shut down the local stack.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

echo "Stopping all compose services..."
docker compose down

echo "Services stopped."
