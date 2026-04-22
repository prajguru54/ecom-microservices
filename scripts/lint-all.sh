#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVICES=(
  "auth-service"
  "gateway-service"
  "catalog-service"
  "cart-service"
  "order-service"
  "inventory-service"
  "notification-service"
)

for service in "${SERVICES[@]}"; do
  SERVICE_DIR="${REPO_ROOT}/services/${service}"
  if [[ -d "${SERVICE_DIR}" && -f "${SERVICE_DIR}/.venv/bin/activate" ]]; then
    echo "Linting ${service}..."
    cd "${SERVICE_DIR}"
    source .venv/bin/activate
    if command -v ruff >/dev/null 2>&1; then
      ruff check .
    else
      echo "ruff not installed in ${service}. Skipping."
    fi
  fi
done

echo "Lint run completed."
