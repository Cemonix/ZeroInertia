from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine
from app.core.logging import logger, setup_logging
from app.core.settings.app_settings import AppSettings

# Load settings
app_settings = AppSettings()  # pyright: ignore[reportCallIssue]

# Setup logging
setup_logging(app_settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    logger.info("Starting up Zero Inertia API...")
    yield
    logger.info("Shutting down Zero Inertia API...")
    await engine.dispose()


app = FastAPI(
    title=app_settings.project_name,
    description="Intelligent to-do list application with AI integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Zero Inertia API is running"}

# API routes will be added here
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.reload,
        log_level=app_settings.log_level,
    )
