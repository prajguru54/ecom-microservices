"""Rate limiting middleware using Redis."""

import logging
import time
from typing import Callable

import redis.asyncio as redis
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis sliding window."""
    
    def __init__(self, app, settings=None):
        super().__init__(app)
        self.settings = settings or get_settings()
        self.redis_client = redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiting middleware."""
        # Get client identifier (IP address or user ID if authenticated)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not await self._is_request_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self.settings.rate_limit_window
                },
                headers={
                    "Retry-After": str(self.settings.rate_limit_window),
                    "X-RateLimit-Limit": str(self.settings.rate_limit_requests),
                    "X-RateLimit-Window": str(self.settings.rate_limit_window)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining_requests = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.settings.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Window"] = str(self.settings.rate_limit_window)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use user ID if authenticated
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user['user_id']}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for forwarded IP headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            client_ip = real_ip.strip()
        
        return f"ip:{client_ip}"
    
    async def _is_request_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit."""
        try:
            current_time = int(time.time())
            window_start = current_time - self.settings.rate_limit_window
            
            key = f"rate_limit:{client_id}"
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Use a unique member so same-second requests are all counted.
            request_member = f"{current_time}:{time.time_ns()}"
            pipe.zadd(key, {request_member: current_time})
            
            # Set expiry
            pipe.expire(key, self.settings.rate_limit_window + 10)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            return current_requests < self.settings.rate_limit_requests
            
        except Exception as e:
            logger.error(f"Rate limit check failed for {client_id}: {str(e)}")
            # Allow request on Redis errors to avoid breaking the service
            return True
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client in current window."""
        try:
            current_time = int(time.time())
            window_start = current_time - self.settings.rate_limit_window
            
            key = f"rate_limit:{client_id}"
            current_requests = await self.redis_client.zcount(key, window_start, current_time)
            
            return max(0, self.settings.rate_limit_requests - current_requests)
            
        except Exception as e:
            logger.error(f"Failed to get remaining requests for {client_id}: {str(e)}")
            return self.settings.rate_limit_requests