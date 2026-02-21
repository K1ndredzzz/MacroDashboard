"""
FastAPI application main entry point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.v1 import indicators, health, simulation, events

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Configure CORS
# Allow all origins in development, or specify allowed origins
import os
allowed_origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8080",
    "http://localhost:8020",  # API port
    "http://localhost:8021",  # Frontend port
]

# Add custom origins from environment variable
custom_origins = os.getenv("CORS_ORIGINS", "")
if custom_origins:
    allowed_origins.extend(custom_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["health"]
)

app.include_router(
    indicators.router,
    prefix=settings.API_V1_PREFIX,
    tags=["indicators"]
)

app.include_router(
    simulation.router,
    prefix=f"{settings.API_V1_PREFIX}/simulation",
    tags=["simulation"]
)

app.include_router(
    events.router,
    prefix=f"{settings.API_V1_PREFIX}/events",
    tags=["events"]
)


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Project: {settings.GCP_PROJECT_ID}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }
