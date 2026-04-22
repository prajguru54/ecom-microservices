"""Tests for auth service endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Test client fixture."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_registration(client):
    """Test user registration endpoint."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_user_login(client):
    """Test user login endpoint."""
    # First register a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }
    client.post("/auth/register", json=user_data)
    
    # Then try to login
    login_data = {
        "username": "testuser",
        "password": "testpassword123",
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_token_validation(client):
    """Test token validation endpoint."""
    # Register and login to get a token
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }
    client.post("/auth/register", json=user_data)
    
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword123",
    })
    token = login_response.json()["access_token"]
    
    # Validate the token
    validation_response = client.post("/auth/validate", json={"token": token})
    assert validation_response.status_code == 200
    data = validation_response.json()
    assert data["valid"] is True
    assert "user_id" in data
    assert data["username"] == "testuser"


def test_duplicate_registration(client):
    """Test that duplicate registration fails."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }
    
    # First registration should succeed
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration should fail
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400


def test_invalid_login(client):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistentuser",
        "password": "wrongpassword",
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401