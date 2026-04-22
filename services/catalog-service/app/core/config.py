"""
Configuration settings for the catalog service.
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    SERVICE_NAME: str = Field(default="catalog-service", description="Service name")
    SERVICE_PORT: int = Field(default=8004, description="Service port")
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://ecom_user:change_me@localhost:5432/catalog_db",
        description="Database URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL"
    )
    
    # Cache settings
    CACHE_TTL_SECONDS: int = Field(default=300, description="Default cache TTL in seconds")
    PRODUCT_CACHE_TTL: int = Field(default=600, description="Product cache TTL in seconds")
    CATEGORY_CACHE_TTL: int = Field(default=900, description="Category cache TTL in seconds")
    
    # Pagination settings
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default pagination page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum pagination page size")
    
    model_config = {"env_file": ".env"}


settings = Settings()