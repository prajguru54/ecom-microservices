#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <service-name>"
  echo "Example: $0 auth-service"
  exit 1
fi

SERVICE_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_DIR="${REPO_ROOT}/services/${SERVICE_NAME}"

if [[ ! -d "${SERVICE_DIR}" ]]; then
  echo "Service directory not found: ${SERVICE_DIR}"
  exit 1
fi

if [[ ! -f "${SERVICE_DIR}/alembic.ini" ]]; then
  echo "alembic.ini not found in ${SERVICE_NAME}. Skipping."
  exit 0
fi

if [[ ! -f "${SERVICE_DIR}/.venv/bin/activate" ]]; then
  echo "Missing virtual env for ${SERVICE_NAME}. Expected at ${SERVICE_DIR}/.venv. Skipping."
  exit 0
fi

cd "${SERVICE_DIR}"
source .venv/bin/activate
alembic upgrade head

echo "Applied migrations for ${SERVICE_NAME}."
