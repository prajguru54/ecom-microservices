#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVICES=(
  "auth-service"
  "catalog-service"
  "cart-service"
  "order-service"
  "inventory-service"
  "notification-service"
  "gateway-service"
)

for service in "${SERVICES[@]}"; do
  "${SCRIPT_DIR}/migrate-service.sh" "${service}"
done

echo "Migration pass completed."
