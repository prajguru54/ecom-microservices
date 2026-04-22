#!/usr/bin/env bash
set -euo pipefail

# Runs service-level tests for each backend service that has a local .venv.
# Complements scripts/lint-all.sh in the validation flow.
# After tests pass, use scripts/smoke-test.sh for basic runtime checks.

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
    echo "Running tests for ${service}..."
    cd "${SERVICE_DIR}"
    source .venv/bin/activate
    if command -v pytest >/dev/null 2>&1; then
      pytest -q
    else
      echo "pytest not installed in ${service}. Skipping."
    fi
  fi
done

echo "Test run completed."
