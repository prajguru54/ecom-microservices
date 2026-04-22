"""
Product repository for database operations.
"""
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Product repository with specific operations."""
    
    def __init__(self):
        """Initialize product repository."""
        super().__init__(Product)
    
    async def get_with_category(self, db: AsyncSession, id: int) -> Optional[Product]:
        """Get product by ID with category information."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.category))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi_with_category(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get multiple products with category information."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.category))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_category(
        self, 
        db: AsyncSession, 
        category_id: int, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Product]:
        """Get products by category."""
        query = select(self.model).where(self.model.category_id == category_id)
        
        if active_only:
            query = query.where(self.model.is_active == True)  # noqa: E712
        
        result = await db.execute(
            query.options(selectinload(self.model.category))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def search_by_name(
        self, 
        db: AsyncSession, 
        name: str, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Product]:
        """Search products by name."""
        query = select(self.model).where(
            self.model.name.ilike(f"%{name}%")
        )
        
        if active_only:
            query = query.where(self.model.is_active == True)  # noqa: E712
        
        result = await db.execute(
            query.options(selectinload(self.model.category))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_price_range(
        self,
        db: AsyncSession,
        min_price: float = None,
        max_price: float = None,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Product]:
        """Get products within price range."""
        conditions = []
        
        if min_price is not None:
            conditions.append(self.model.price >= min_price)
        
        if max_price is not None:
            conditions.append(self.model.price <= max_price)
        
        if active_only:
            conditions.append(self.model.is_active == True)  # noqa: E712
        
        query = select(self.model)
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(
            query.options(selectinload(self.model.category))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_active_products(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get only active products."""
        result = await db.execute(
            select(self.model)
            .where(self.model.is_active == True)  # noqa: E712
            .options(selectinload(self.model.category))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# Global repository instance
product_repository = ProductRepository()