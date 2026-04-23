# Relative path: services/gateway-service/.env

"""Configuration settings for the Gateway Service."""

from functools import lru_cache
from typing import Annotated, Any, Dict, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Gateway Service"
    debug: bool = False
    port: int = 8003
    host: str = "0.0.0.0"

    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # CORS
    cors_origins: Annotated[List[str], NoDecode] = ["*"]
    cors_methods: Annotated[List[str], NoDecode] = ["*"]
    cors_headers: Annotated[List[str], NoDecode] = ["*"]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Service Discovery
    auth_service_url: str
    catalog_service_url: str
    cart_service_url: str
    order_service_url: str
    inventory_service_url: str

    # Redis for rate limiting and caching
    redis_url: str

    # Logging
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("cors_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v: str | List[str]) -> List[str]:
        """Parse CORS methods from comma-separated string."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("cors_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v: str | List[str]) -> List[str]:
        """Parse CORS headers from comma-separated string."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Service Registry Configuration
# upstream_prefix: when strip_prefix is True, the path after the gateway prefix is appended
# to this path on the target service (e.g. /api/products/1 -> /products/1 on catalog-service).
SERVICE_ROUTES: Dict[str, Dict[str, Any]] = {
    "auth": {
        "prefix": "/auth",
        "service_url_key": "auth_service_url",
        "strip_prefix": True,
        "upstream_prefix": "/auth",
    },
    "catalog": {
        "prefix": "/api/products",
        "service_url_key": "catalog_service_url",
        "strip_prefix": True,
        "upstream_prefix": "/products",
    },
    "catalog_categories": {
        "prefix": "/api/categories",
        "service_url_key": "catalog_service_url",
        "strip_prefix": True,
        "upstream_prefix": "/categories",
    },
    "cart": {
        "prefix": "/api/cart",
        "service_url_key": "cart_service_url",
        "strip_prefix": True,
    },
    "order": {
        "prefix": "/api/orders",
        "service_url_key": "order_service_url",
        "strip_prefix": True,
    },
    "inventory": {
        "prefix": "/api/inventory",
        "service_url_key": "inventory_service_url",
        "strip_prefix": True,
    },
}

# Routes that don't require authentication
PUBLIC_ROUTES: List[str] = [
    "/",
    "/auth/login",
    "/auth/register",
    "/api/products",  # Allow public product browsing
    "/api/categories",  # Allow public category browsing (exact path + nested via prefix rule)
    "/health",
    "/docs",
    "/openapi.json",
]
