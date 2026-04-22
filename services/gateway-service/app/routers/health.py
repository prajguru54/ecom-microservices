"""Health check endpoints for the Gateway Service."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from ..core.service_registry import ServiceRegistry, get_service_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Basic health check for the gateway service."""
    return {
        "status": "healthy",
        "service": "gateway-service",
        "version": "1.0.0"
    }


@router.get("/services", status_code=status.HTTP_200_OK)
async def health_check_services(
    service_registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """Health check for all backend services."""
    try:
        health_status = await service_registry.health_check_all()
        
        return {
            "gateway": {
                "status": "healthy",
                "service": "gateway-service"
            },
            **health_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "gateway": {
                "status": "healthy",
                "service": "gateway-service"
            },
            "status": "error",
            "error": "Failed to check backend services"
        }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(
    service_registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """Readiness check - gateway is ready when it can reach critical services."""
    try:
        # Check critical services (auth is essential)
        auth_health = await service_registry.health_check("auth")
        
        if auth_health["status"] == "healthy":
            return {
                "status": "ready",
                "service": "gateway-service",
                "critical_services": {
                    "auth": auth_health["status"]
                }
            }
        else:
            return {
                "status": "not_ready",
                "service": "gateway-service",
                "reason": "Auth service is not healthy",
                "critical_services": {
                    "auth": auth_health["status"]
                }
            }
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "status": "not_ready",
            "service": "gateway-service",
            "reason": "Failed to check service dependencies"
        }