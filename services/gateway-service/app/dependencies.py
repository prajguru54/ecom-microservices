# Relative path: services/gateway-service/.env

"""Dependency injection for the Gateway Service."""

from functools import lru_cache
from typing import Optional

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.config import Settings, get_settings


# Redis connection
@lru_cache()
def get_redis_client(settings: Settings = Depends(get_settings)) -> redis.Redis:
    """Get Redis client for rate limiting and caching."""
    return redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


# JWT Bearer token dependency
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings)
) -> Optional[dict]:
    """Extract user information from JWT token if present."""
    if not credentials:
        return None
    
    try:
        import jwt
        
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email")
        }
    except jwt.InvalidTokenError:
        return None


async def require_auth(
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """Require authentication for protected routes."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user