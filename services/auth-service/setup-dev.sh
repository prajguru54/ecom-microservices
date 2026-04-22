#!/usr/bin/env bash
set -euo pipefail

# Env file path: services/auth-service/setup-dev.sh

echo "Setting up auth-service for development..."

# Create virtual environment if it doesn't exist
if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Install dev dependencies
echo "Installing dev dependencies..."
pip install -e ".[dev]"

echo "Auth service development setup complete!"
echo ""
echo "To activate the environment: source .venv/bin/activate"
echo "To run the service: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
echo "To run tests: pytest"
echo "To generate migration: alembic revision --autogenerate -m 'Create users table'"
echo "To apply migrations: alembic upgrade head"