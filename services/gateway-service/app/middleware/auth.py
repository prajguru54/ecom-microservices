"""JWT Authentication Middleware for the Gateway Service."""

import logging
from typing import Callable, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import PUBLIC_ROUTES, get_settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT Authentication middleware for protecting routes."""
    
    def __init__(self, app, settings=None):
        super().__init__(app)
        self.settings = settings or get_settings()
        self.public_routes = set(PUBLIC_ROUTES)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through auth middleware."""
        path = request.url.path
        method = request.method
        
        # Skip authentication for public routes
        if self._is_public_route(path, method):
            logger.debug(f"Public route accessed: {method} {path}")
            return await call_next(request)
        
        # Extract and validate JWT token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Missing or invalid authorization header for: {method} {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        user_info = await self._validate_token(token)
        
        if not user_info:
            logger.warning(f"Invalid token for: {method} {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Add user info to request state
        request.state.user = user_info
        logger.debug(f"Authenticated user {user_info.get('user_id')} for: {method} {path}")
        
        return await call_next(request)
    
    def _is_public_route(self, path: str, method: str) -> bool:
        """Check if route is public and doesn't require authentication."""
        # Check exact matches
        if path in self.public_routes:
            return True
        
        # Check prefix matches for GET requests to products
        if method == "GET" and path.startswith("/api/products"):
            return True

        # Public category reads (nested paths e.g. /api/categories/root)
        if method == "GET" and path.startswith("/api/categories"):
            return True

        # Check for health checks and docs
        if path.startswith("/health") or path in ["/docs", "/openapi.json", "/redoc"]:
            return True
        
        return False
    
    async def _validate_token(self, token: str) -> Optional[dict]:
        """Validate JWT token and extract user information."""
        try:
            import jwt
            
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            return {
                "user_id": user_id,
                "username": payload.get("username"),
                "email": payload.get("email"),
                "exp": payload.get("exp")
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None