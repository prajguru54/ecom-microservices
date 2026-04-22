"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis_client
from app.database import get_db

router = APIRouter()


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "catalog-service",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check with database connectivity.
    """
    try:
        # Check database connectivity
        await db.execute("SELECT 1")
        
        # Check Redis connectivity
        redis_client = await get_redis_client()
        await redis_client.ping()
        
        return {
            "status": "ready",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )