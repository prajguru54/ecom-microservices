"""
Product management endpoints.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import (
    delete_pattern_from_cache,
    get_from_cache,
    make_cache_key,
    set_in_cache,
)
from app.core.config import settings
from app.database import get_db
from app.repositories.category import category_repository
from app.repositories.product import product_repository
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Number of records to return"
    ),
    search: str = Query(None, description="Search term for product names"),
    category_id: int = Query(None, description="Filter by category ID"),
    min_price: float = Query(None, ge=0, description="Minimum price filter"),
    max_price: float = Query(None, ge=0, description="Maximum price filter"),
    active_only: bool = Query(True, description="Show only active products"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get products with optional filtering and pagination.
    """
    # Create cache key based on parameters
    cache_key = make_cache_key(
        "products",
        f"skip_{skip}",
        f"limit_{limit}",
        f"search_{search or 'none'}",
        f"category_{category_id or 'none'}",
        f"min_{min_price or 'none'}",
        f"max_{max_price or 'none'}",
        f"active_{active_only}"
    )
    
    # Try to get from cache
    cached_products = await get_from_cache(cache_key)
    if cached_products is not None:
        return [ProductResponse(**prod) for prod in cached_products]
    
    # Get from database based on filters
    if search:
        products = await product_repository.search_by_name(
            db, search, skip, limit, active_only
        )
    elif category_id is not None:
        products = await product_repository.get_by_category(
            db, category_id, skip, limit, active_only
        )
    elif min_price is not None or max_price is not None:
        products = await product_repository.get_by_price_range(
            db, min_price, max_price, skip, limit, active_only
        )
    elif active_only:
        products = await product_repository.get_active_products(db, skip, limit)
    else:
        products = await product_repository.get_multi_with_category(db, skip, limit)
    
    # Convert to response format
    response_products = [ProductResponse.model_validate(prod) for prod in products]
    
    # Cache the result
    await set_in_cache(
        cache_key,
        [prod.model_dump() for prod in response_products],
        ttl=settings.PRODUCT_CACHE_TTL
    )
    
    return response_products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific product by ID.
    """
    cache_key = make_cache_key("product", str(product_id))
    
    # Try to get from cache
    cached_product = await get_from_cache(cache_key)
    if cached_product is not None:
        return ProductResponse(**cached_product)
    
    # Get from database
    product = await product_repository.get_with_category(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    response_product = ProductResponse.model_validate(product)
    
    # Cache the result
    await set_in_cache(
        cache_key,
        response_product.model_dump(),
        ttl=settings.PRODUCT_CACHE_TTL
    )
    
    return response_product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new product.
    """
    # Verify that the category exists
    category = await category_repository.get(db, product.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Create product
    db_product = await product_repository.create(db, product.model_dump())
    
    # Get the created product with category information
    created_product = await product_repository.get_with_category(db, db_product.id)
    
    # Invalidate related caches
    await delete_pattern_from_cache("products:*")
    
    return ProductResponse.model_validate(created_product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing product.
    """
    # Get existing product
    db_product = await product_repository.get(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Verify category exists if category_id is being updated
    if product.category_id is not None:
        category = await category_repository.get(db, product.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    
    # Update product
    update_data = product.model_dump(exclude_unset=True)
    updated_product = await product_repository.update(db, db_product, update_data)
    
    # Get the updated product with category information
    product_with_category = await product_repository.get_with_category(db, product_id)
    
    # Invalidate related caches
    await delete_pattern_from_cache("products:*")
    await delete_pattern_from_cache(f"product:{product_id}")
    
    return ProductResponse.model_validate(product_with_category)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a product.
    """
    # Check if product exists
    product = await product_repository.get(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Delete product
    await product_repository.delete(db, product_id)
    
    # Invalidate related caches
    await delete_pattern_from_cache("products:*")
    await delete_pattern_from_cache(f"product:{product_id}")
    
    return {"message": "Product deleted successfully"}


@router.get("/category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Number of records to return"
    ),
    active_only: bool = Query(True, description="Show only active products"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get products by category ID.
    """
    cache_key = make_cache_key(
        "products",
        "category",
        str(category_id),
        f"skip_{skip}",
        f"limit_{limit}",
        f"active_{active_only}"
    )
    
    # Try to get from cache
    cached_products = await get_from_cache(cache_key)
    if cached_products is not None:
        return [ProductResponse(**prod) for prod in cached_products]
    
    # Verify that the category exists
    category = await category_repository.get(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Get products by category
    products = await product_repository.get_by_category(
        db, category_id, skip, limit, active_only
    )
    
    # Convert to response format
    response_products = [ProductResponse.model_validate(prod) for prod in products]
    
    # Cache the result
    await set_in_cache(
        cache_key,
        [prod.model_dump() for prod in response_products],
        ttl=settings.PRODUCT_CACHE_TTL
    )
    
    return response_products


@router.get("/search/{search_term}", response_model=List[ProductResponse])
async def search_products(
    search_term: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Number of records to return"
    ),
    active_only: bool = Query(True, description="Show only active products"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search products by name.
    """
    cache_key = make_cache_key(
        "products",
        "search",
        search_term,
        f"skip_{skip}",
        f"limit_{limit}",
        f"active_{active_only}"
    )
    
    # Try to get from cache
    cached_products = await get_from_cache(cache_key)
    if cached_products is not None:
        return [ProductResponse(**prod) for prod in cached_products]
    
    # Search products
    products = await product_repository.search_by_name(
        db, search_term, skip, limit, active_only
    )
    
    # Convert to response format
    response_products = [ProductResponse.model_validate(prod) for prod in products]
    
    # Cache the result
    await set_in_cache(
        cache_key,
        [prod.model_dump() for prod in response_products],
        ttl=settings.PRODUCT_CACHE_TTL
    )
    
    return response_products