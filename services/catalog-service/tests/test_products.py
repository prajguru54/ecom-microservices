"""
Tests for product endpoints.
"""
import pytest
from decimal import Decimal
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

MOCK_PRODUCT = {
    "id": 1,
    "name": "iPhone 15",
    "description": "Latest iPhone model",
    "price": "999.99",
    "category_id": 1,
    "is_active": True,
    "created_at": "2026-04-22T14:00:00",
    "updated_at": "2026-04-22T14:00:00",
    "category": MOCK_CATEGORY
}

MOCK_PRODUCTS = [
    MOCK_PRODUCT,
    {
        "id": 2,
        "name": "Samsung Galaxy S24",
        "description": "Latest Samsung phone",
        "price": "899.99",
        "category_id": 1,
        "is_active": True,
        "created_at": "2026-04-22T14:00:00",
        "updated_at": "2026-04-22T14:00:00",
        "category": MOCK_CATEGORY
    }
]


@patch('app.repositories.product.product_repository.get_active_products')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_products(mock_get_db, mock_cache, mock_get_active):
    """Test getting products."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get_active.return_value = MOCK_PRODUCTS
    
    response = client.get("/products/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "iPhone 15"


@patch('app.repositories.product.product_repository.get_with_category')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_product_by_id(mock_get_db, mock_cache, mock_get_with_cat):
    """Test getting a product by ID."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get_with_cat.return_value = MOCK_PRODUCT
    
    response = client.get("/products/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "iPhone 15"
    assert data["id"] == 1
    assert data["category"]["name"] == "Electronics"


@patch('app.repositories.product.product_repository.get_with_category')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_product_not_found(mock_get_db, mock_cache, mock_get_with_cat):
    """Test getting a product that doesn't exist."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get_with_cat.return_value = None  # Product not found
    
    response = client.get("/products/999")
    assert response.status_code == 404
    
    data = response.json()
    assert "Product not found" in data["detail"]


@patch('app.repositories.product.product_repository.get_with_category')
@patch('app.repositories.product.product_repository.create')
@patch('app.repositories.category.category_repository.get')
@patch('app.database.get_db')
def test_create_product(mock_get_db, mock_get_category, mock_create, mock_get_with_cat):
    """Test creating a new product."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_get_category.return_value = MOCK_CATEGORY  # Category exists
    
    # Mock the created product (without category first)
    class MockProduct:
        def __init__(self):
            self.id = 1
            self.name = "iPhone 15"
            self.description = "Latest iPhone model"
            self.price = Decimal("999.99")
            self.category_id = 1
            self.is_active = True
    
    mock_create.return_value = MockProduct()
    
    # Mock getting the product with category after creation
    mock_get_with_cat.return_value = MOCK_PRODUCT
    
    product_data = {
        "name": "iPhone 15",
        "description": "Latest iPhone model",
        "price": "999.99",
        "category_id": 1,
        "is_active": True
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "iPhone 15"
    assert data["id"] == 1
    assert data["category"]["name"] == "Electronics"


@patch('app.repositories.category.category_repository.get')
@patch('app.database.get_db')
def test_create_product_invalid_category(mock_get_db, mock_get_category):
    """Test creating a product with non-existent category."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_get_category.return_value = None  # Category doesn't exist
    
    product_data = {
        "name": "iPhone 15",
        "description": "Latest iPhone model",
        "price": "999.99",
        "category_id": 999,  # Non-existent category
        "is_active": True
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "Category not found" in data["detail"]


def test_create_product_invalid_data():
    """Test creating a product with invalid data."""
    product_data = {
        "name": "",  # Empty name
        "price": -10,  # Negative price
        "category_id": 1
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422  # Validation error


@patch('app.repositories.product.product_repository.search_by_name')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_search_products(mock_get_db, mock_cache, mock_search):
    """Test searching products by name."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_search.return_value = [MOCK_PRODUCT]
    
    response = client.get("/products/search/iPhone")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "iPhone 15"


@patch('app.repositories.product.product_repository.get_by_category')
@patch('app.repositories.category.category_repository.get')
@patch('app.core.cache.get_from_cache')
@patch('app.database.get_db')
def test_get_products_by_category(mock_get_db, mock_cache, mock_get_category, mock_get_by_cat):
    """Test getting products by category."""
    # Mock dependencies
    mock_get_db.return_value.__aenter__ = AsyncMock()
    mock_get_db.return_value.__aexit__ = AsyncMock()
    mock_cache.return_value = None  # Cache miss
    mock_get_category.return_value = MOCK_CATEGORY  # Category exists
    mock_get_by_cat.return_value = MOCK_PRODUCTS
    
    response = client.get("/products/category/1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(product["category_id"] == 1 for product in data)