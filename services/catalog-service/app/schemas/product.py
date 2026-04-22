"""
Pydantic schemas for product operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse


class ProductBase(BaseModel):
    """Base product schema."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price")
    category_id: int = Field(..., description="Category ID")
    is_active: bool = Field(default=True, description="Whether product is active")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[Decimal] = Field(None, gt=0, description="Product price")
    category_id: Optional[int] = Field(None, description="Category ID")
    is_active: Optional[bool] = Field(None, description="Whether product is active")


class ProductResponse(ProductBase):
    """Schema for product response."""
    
    id: int = Field(..., description="Product ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    category: Optional[CategoryResponse] = Field(None, description="Category information")
    
    model_config = {"from_attributes": True}