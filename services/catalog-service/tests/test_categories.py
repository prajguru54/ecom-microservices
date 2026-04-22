"""
Tests for category endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)


# Mock data
MOCK_CATEGORY = {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic products",
    "parent_id": None,
    "created_at": "2026-04-22T14:00:00",
    "updated_at": "2026-04-22T14:00:00"
}

MOCK_CATEGORIES = [
    MOCK_CATEGORY,
    {
        "id": 2,
        "name": "Smartphones",
        "description": "Mobile phones",
        "parent_id": 1,
        "created_at": "2026-04-22T14:00:00",
        "updated_at": "2026-04-22T14:00:00"
    }
]


@patch('app.repositories.category.category_repository.get_multi')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_categories(mock_get_db, mock_cache, mock_get_multi):
    """Test getting categories."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get_multi.return_value = MOCK_CATEGORIES
    
    response = client.get("/categories/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Electronics"


@patch('app.repositories.category.category_repository.get')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_category_by_id(mock_get_db, mock_cache, mock_get):
    """Test getting a category by ID."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get.return_value = MOCK_CATEGORY
    
    response = client.get("/categories/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Electronics"
    assert data["id"] == 1


@patch('app.repositories.category.category_repository.get')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_category_not_found(mock_get_db, mock_cache, mock_get):
    """Test getting a category that doesn't exist."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get.return_value = None  # Category not found
    
    response = client.get("/categories/999")
    assert response.status_code == 404
    
    data = response.json()
    assert "Category not found" in data["detail"]


@patch('app.repositories.category.category_repository.create')
@patch('app.repositories.category.category_repository.get_by_name')
@patch('app.database.get_db')
def test_create_category(mock_get_db, mock_get_by_name, mock_create):
    """Test creating a new category."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_get_by_name.return_value = None  # Name doesn't exist
    mock_create.return_value = MOCK_CATEGORY
    
    category_data = {
        "name": "Electronics",
        "description": "Electronic products",
        "parent_id": None
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Electronics"
    assert data["id"] == 1


@patch('app.repositories.category.category_repository.get_by_name')
@patch('app.database.get_db')
def test_create_category_duplicate_name(mock_get_db, mock_get_by_name):
    """Test creating a category with duplicate name."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_get_by_name.return_value = MOCK_CATEGORY  # Name already exists
    
    category_data = {
        "name": "Electronics",
        "description": "Electronic products",
        "parent_id": None
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "Category with this name already exists" in data["detail"]


def test_create_category_invalid_data():
    """Test creating a category with invalid data."""
    category_data = {
        "name": "",  # Empty name
        "description": "Electronic products"
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 422  # Validation error