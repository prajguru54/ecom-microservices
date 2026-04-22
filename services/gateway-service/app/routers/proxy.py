"""Proxy router for forwarding requests to backend services."""

import logging

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse

from ..core.config import SERVICE_ROUTES
from ..core.service_registry import ServiceRegistry

logger = logging.getLogger(__name__)


async def proxy_request(
    request: Request,
    service_name: str,
    path: str,
    service_registry: ServiceRegistry,
) -> Response:
    """Proxy a request to a backend service."""
    try:
        # Get HTTP client for the service
        client = await service_registry.get_client(service_name)
        
        # Prepare request data
        method = request.method
        headers = dict(request.headers)
        
        # Remove hop-by-hop headers
        hop_by_hop_headers = {
            'connection', 'keep-alive', 'proxy-authenticate',
            'proxy-authorization', 'te', 'trailers', 'upgrade'
        }
        headers = {k: v for k, v in headers.items() 
                  if k.lower() not in hop_by_hop_headers}
        
        # Add user info to headers if available
        if hasattr(request.state, 'user') and request.state.user:
            user = request.state.user
            headers['X-User-ID'] = str(user['user_id'])
            headers['X-Username'] = user.get('username', '')
            headers['X-User-Email'] = user.get('email', '')
        
        # Get request body
        body = None
        if method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
        
        # Build query parameters
        query_params = dict(request.query_params)
        
        logger.info(f"Proxying {method} {path} to {service_name} service")
        
        # Make request to backend service
        response = await client.request(
            method=method,
            url=path,
            headers=headers,
            content=body,
            params=query_params
        )
        
        # Prepare response headers
        response_headers = dict(response.headers)
        
        # Remove hop-by-hop headers from response
        response_headers = {k: v for k, v in response_headers.items()
                          if k.lower() not in hop_by_hop_headers}
        
        # Handle streaming response for large files
        if response.headers.get('content-type', '').startswith('application/octet-stream'):
            return StreamingResponse(
                response.aiter_bytes(),
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get('content-type')
            )
        
        # Return regular response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get('content-type')
        )
        
    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to {service_name} service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service {service_name} is currently unavailable"
        )
    except httpx.TimeoutException as e:
        logger.error(f"Timeout connecting to {service_name} service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Service {service_name} timed out"
        )
    except Exception as e:
        logger.error(f"Error proxying request to {service_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Internal proxy error"
        )


def register_proxy_routes(app: FastAPI):
    """Register all proxy routes with the FastAPI app."""
    
    for service_name, route_config in SERVICE_ROUTES.items():
        prefix = route_config["prefix"]
        strip_prefix = route_config.get("strip_prefix", False)
        
        def make_proxy_handler(svc_name: str, should_strip: bool):
            """Create a proxy handler for a specific service."""
            async def proxy_handler(request: Request, path: str = ""):
                # Determine the target path
                target_path = request.url.path
                if should_strip:
                    target_path = f"/{path}" if path else "/"

                service_registry = request.app.state.service_registry

                if not target_path.startswith("/"):
                    target_path = f"/{target_path}"

                return await proxy_request(
                    request=request,
                    service_name=svc_name,
                    path=target_path,
                    service_registry=service_registry,
                )
            
            return proxy_handler
        
        # Create the handler
        handler = make_proxy_handler(service_name, strip_prefix)
        
        # Add route with catch-all path
        route_path = f"{prefix}/{{path:path}}"
        
        # Add exact prefix match route
        app.add_api_route(
            prefix,
            handler,
            methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            name=f"proxy_{service_name}_root",
            include_in_schema=False
        )
        
        # Add catch-all route for paths under the prefix
        app.add_api_route(
            route_path,
            handler,
            methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            name=f"proxy_{service_name}",
            include_in_schema=False
        )