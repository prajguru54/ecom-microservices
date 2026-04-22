"""
Category management endpoints.
"""
from typing import List

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
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Number of records to return"
    ),
    search: str = Query(None, description="Search term for category names"),
    parent_id: int = Query(None, description="Filter by parent category ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get categories with optional filtering and pagination.
    """
    # Create cache key based on parameters
    cache_key = make_cache_key(
        "categories",
        f"skip_{skip}",
        f"limit_{limit}",
        f"search_{search or 'none'}",
        f"parent_{parent_id or 'none'}"
    )
    
    # Try to get from cache
    cached_categories = await get_from_cache(cache_key)
    if cached_categories is not None:
        return [CategoryResponse(**cat) for cat in cached_categories]
    
    # Get from database
    if search:
        categories = await category_repository.search_by_name(db, search, skip, limit)
    elif parent_id is not None:
        categories = await category_repository.get_children(db, parent_id)
        # Apply pagination manually for children
        categories = categories[skip:skip + limit]
    else:
        categories = await category_repository.get_multi(db, skip, limit)
    
    # Convert to response format
    response_categories = [CategoryResponse.model_validate(cat) for cat in categories]
    
    # Cache the result
    await set_in_cache(
        cache_key, 
        [cat.model_dump() for cat in response_categories],
        ttl=settings.CATEGORY_CACHE_TTL
    )
    
    return response_categories


@router.get("/root", response_model=List[CategoryResponse])
async def get_root_categories(db: AsyncSession = Depends(get_db)):
    """
    Get root categories (categories without parent).
    """
    cache_key = make_cache_key("categories", "root")
    
    # Try to get from cache
    cached_categories = await get_from_cache(cache_key)
    if cached_categories is not None:
        return [CategoryResponse(**cat) for cat in cached_categories]
    
    # Get from database
    categories = await category_repository.get_root_categories(db)
    response_categories = [CategoryResponse.model_validate(cat) for cat in categories]
    
    # Cache the result
    await set_in_cache(
        cache_key,
        [cat.model_dump() for cat in response_categories],
        ttl=settings.CATEGORY_CACHE_TTL
    )
    
    return response_categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category by ID.
    """
    cache_key = make_cache_key("category", str(category_id))
    
    # Try to get from cache
    cached_category = await get_from_cache(cache_key)
    if cached_category is not None:
        return CategoryResponse(**cached_category)
    
    # Get from database
    category = await category_repository.get(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    response_category = CategoryResponse.model_validate(category)
    
    # Cache the result
    await set_in_cache(
        cache_key,
        response_category.model_dump(),
        ttl=settings.CATEGORY_CACHE_TTL
    )
    
    return response_category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category.
    """
    # Check if category name already exists
    existing_category = await category_repository.get_by_name(db, category.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    # Create category
    db_category = await category_repository.create(db, category.model_dump())
    
    # Invalidate related caches
    await delete_pattern_from_cache("categories:*")
    
    return CategoryResponse.model_validate(db_category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing category.
    """
    # Get existing category
    db_category = await category_repository.get(db, category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check for name conflicts if name is being updated
    if category.name and category.name != db_category.name:
        existing_category = await category_repository.get_by_name(db, category.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    # Update category
    update_data = category.model_dump(exclude_unset=True)
    updated_category = await category_repository.update(db, db_category, update_data)
    
    # Invalidate related caches
    await delete_pattern_from_cache("categories:*")
    await delete_pattern_from_cache(f"category:{category_id}")
    
    return CategoryResponse.model_validate(updated_category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a category.
    """
    # Check if category exists
    category = await category_repository.get(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Delete category
    await category_repository.delete(db, category_id)
    
    # Invalidate related caches
    await delete_pattern_from_cache("categories:*")
    await delete_pattern_from_cache(f"category:{category_id}")
    
    return {"message": "Category deleted successfully"}


@router.get("/{category_id}/children", response_model=List[CategoryResponse])
async def get_category_children(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get child categories of a specific category.
    """
    cache_key = make_cache_key("category", str(category_id), "children")
    
    # Try to get from cache
    cached_children = await get_from_cache(cache_key)
    if cached_children is not None:
        return [CategoryResponse(**cat) for cat in cached_children]
    
    # Check if parent category exists
    parent_category = await category_repository.get(db, category_id)
    if not parent_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent category not found"
        )
    
    # Get children
    children = await category_repository.get_children(db, category_id)
    response_children = [CategoryResponse.model_validate(cat) for cat in children]
    
    # Cache the result
    await set_in_cache(
        cache_key,
        [cat.model_dump() for cat in response_children],
        ttl=settings.CATEGORY_CACHE_TTL
    )
    
    return response_children