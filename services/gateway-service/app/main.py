# Relative path: services/gateway-service/.env

"""Gateway Service - API Gateway for E-commerce Microservices."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.service_registry import ServiceRegistry
from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .routers import health
from .routers.proxy import register_proxy_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name}")
    
    # Initialize service registry
    service_registry = ServiceRegistry(settings)
    app.state.service_registry = service_registry
    
    yield
    
    # Cleanup
    await service_registry.close_clients()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="API Gateway for E-commerce Microservices",
        version="1.0.0",
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware, settings=settings)
    
    # Add authentication middleware
    app.add_middleware(AuthMiddleware, settings=settings)
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Include routers
    app.include_router(health.router)
    
    # Register proxy routes
    register_proxy_routes(app)
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "E-commerce Microservices Gateway",
            "version": "1.0.0",
            "docs_url": "/docs"
        }
    
    return app


# Create the FastAPI app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )