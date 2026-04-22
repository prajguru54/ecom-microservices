"""
Database models package.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered
from app.models.category import Category  # noqa: F401, E402
from app.models.product import Product  # noqa: F401, E402