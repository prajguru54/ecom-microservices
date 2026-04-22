#!/usr/bin/env bash
set -euo pipefail

# Performs quick health checks against running infrastructure endpoints.
# Intended to run after scripts/dev-up.sh to confirm core services are reachable.

check_url() {
  local url="$1"
  if curl -fsS "${url}" >/dev/null 2>&1; then
    echo "PASS ${url}"
  else
    echo "FAIL ${url}"
  fi
}

check_url "http://localhost/health"
check_url "http://localhost:9090/-/healthy"
check_url "http://localhost:3000/api/health"
