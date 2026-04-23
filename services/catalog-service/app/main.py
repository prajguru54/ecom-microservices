"""
Main FastAPI application for the catalog service.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.database import engine
from app.routers import categories, health, products


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events.
    """
    # Startup
    yield

    # Shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="Catalog Service",
        description="Product catalog management service",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add Prometheus instrumentation
    instrumentator = Instrumentator()
    instrumentator.instrument(app)
    instrumentator.expose(app)

    # Include routers
    app.include_router(health.router)
    app.include_router(products.router, prefix="/products", tags=["products"])
    app.include_router(
        categories.router,
        prefix="/categories",
        tags=["categories"],
    )

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
    )
