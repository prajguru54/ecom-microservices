"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.core.service_registry import get_service_registry
from app.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    """Test basic health check."""
    response = client.get("/health/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "gateway-service"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs_url" in data


def test_health_check_services_healthy(client):
    """Test service health check when all services are healthy."""
    # Mock service registry
    mock_registry = AsyncMock()
    mock_registry.health_check_all.return_value = {
        "status": "healthy",
        "services": {
            "auth": {"status": "healthy", "service": "auth"},
            "catalog": {"status": "healthy", "service": "catalog"}
        }
    }
    client.app.dependency_overrides[get_service_registry] = lambda: mock_registry
    
    response = client.get("/health/services")
    
    assert response.status_code == 200
    data = response.json()
    assert data["gateway"]["status"] == "healthy"
    assert data["status"] == "healthy"
    client.app.dependency_overrides.clear()


def test_readiness_check_ready(client):
    """Test readiness check when auth service is healthy."""
    # Mock service registry
    mock_registry = AsyncMock()
    mock_registry.health_check.return_value = {
        "status": "healthy",
        "service": "auth"
    }
    client.app.dependency_overrides[get_service_registry] = lambda: mock_registry
    
    response = client.get("/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["critical_services"]["auth"] == "healthy"
    client.app.dependency_overrides.clear()