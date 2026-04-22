#!/usr/bin/env bash
set -euo pipefail

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
