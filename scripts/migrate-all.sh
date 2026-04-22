#!/usr/bin/env bash
set -euo pipefail

# Runs migrations across all known backend services.
# This script delegates real work to scripts/migrate-service.sh for each service.
# Typical setup order:
#   1) scripts/dev-up.sh
#   2) scripts/init-databases.sh
#   3) scripts/migrate-all.sh

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
