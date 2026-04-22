"""
Category repository for database operations.
"""
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Category repository with specific operations."""
    
    def __init__(self):
        """Initialize category repository."""
        super().__init__(Category)
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Category]:
        """Get category by name."""
        result = await db.execute(
            select(self.model).where(
                func.lower(self.model.name) == name.lower()
            )
        )
        return result.scalar_one_or_none()
    
    async def get_children(self, db: AsyncSession, parent_id: int) -> List[Category]:
        """Get child categories by parent ID."""
        result = await db.execute(
            select(self.model).where(self.model.parent_id == parent_id)
        )
        return list(result.scalars().all())
    
    async def get_root_categories(self, db: AsyncSession) -> List[Category]:
        """Get root categories (categories without parent)."""
        result = await db.execute(
            select(self.model).where(self.model.parent_id.is_(None))
        )
        return list(result.scalars().all())
    
    async def search_by_name(
        self, 
        db: AsyncSession, 
        name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """Search categories by name."""
        result = await db.execute(
            select(self.model)
            .where(self.model.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# Global repository instance
category_repository = CategoryRepository()