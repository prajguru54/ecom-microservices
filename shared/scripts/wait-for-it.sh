#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <host> <port>"
  exit 1
fi

HOST="$1"
PORT="$2"

echo "Waiting for ${HOST}:${PORT}..."
until nc -z "${HOST}" "${PORT}"; do
  sleep 1
done

echo "${HOST}:${PORT} is available."
