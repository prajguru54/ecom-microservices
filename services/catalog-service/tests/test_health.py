"""
Tests for health check endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "catalog-service"
    assert "version" in data


def test_readiness_check():
    """Test readiness check endpoint."""
    # This might fail in test environment without real DB/Redis
    # but we test the endpoint structure
    response = client.get("/health/ready")
    
    # Should be either 200 (if DB/Redis are available) or 503 (if not)
    assert response.status_code in [200, 503]
    
    data = response.json()
    if response.status_code == 200:
        assert data["status"] == "ready"
        assert "database" in data
        assert "redis" in data
    else:
        assert "detail" in data
        assert "Service not ready" in data["detail"]