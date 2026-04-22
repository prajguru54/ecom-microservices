"""Service registry for managing backend service connections."""

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import Request

from .config import SERVICE_ROUTES, Settings, get_settings

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Manages connections to backend services."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._service_urls: Dict[str, str] = {}
        
        # Initialize service URLs
        for service_name, route_config in SERVICE_ROUTES.items():
            url_key = route_config["service_url_key"]
            service_url = getattr(settings, url_key)
            self._service_urls[service_name] = service_url
    
    async def get_client(self, service_name: str) -> httpx.AsyncClient:
        """Get or create HTTP client for a service."""
        if service_name not in self._clients:
            base_url = self._service_urls.get(service_name)
            if not base_url:
                raise ValueError(f"Service '{service_name}' not configured")
            
            self._clients[service_name] = httpx.AsyncClient(
                base_url=base_url,
                timeout=30.0,
                follow_redirects=True
            )
            logger.info(f"Created HTTP client for {service_name} at {base_url}")
        
        return self._clients[service_name]
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the base URL for a service."""
        return self._service_urls.get(service_name)
    
    async def health_check(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service."""
        try:
            client = await self.get_client(service_name)
            response = await client.get("/health")
            
            return {
                "service": service_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all registered services."""
        results = {}
        overall_status = "healthy"
        
        for service_name in SERVICE_ROUTES.keys():
            health = await self.health_check(service_name)
            results[service_name] = health
            
            if health["status"] != "healthy":
                overall_status = "degraded"
        
        return {
            "status": overall_status,
            "services": results
        }
    
    async def close_clients(self):
        """Close all HTTP clients."""
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()
        logger.info("Closed all HTTP clients")


def get_service_registry(request: Request) -> ServiceRegistry:
    """Get the lifespan-managed service registry instance."""
    registry = getattr(request.app.state, "service_registry", None)
    if registry is None:
        settings = get_settings()
        registry = ServiceRegistry(settings)
        request.app.state.service_registry = registry
    return registry