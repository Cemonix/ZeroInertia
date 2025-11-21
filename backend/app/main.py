from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.exception_handlers import app_exception_handler
from app.api.v1 import (
    auth,
    checklist,
    genre,
    label,
    media,
    note,
    notification,
    priority,
    project,
    section,
    statistics,
    streak,
    task,
)
from app.core.database import engine
from app.core.exceptions import AppException
from app.core.logging import logger, setup_logging
from app.core.rate_limit import get_rate_limiter, rate_limit_exceeded_handler
from app.core.scheduler import setup_scheduler
from app.core.seed import seed_database
from app.core.settings.app_settings import get_app_settings
from app.middleware.csrf import CSRFMiddleware

# Load settings
app_settings = get_app_settings()

# Setup logging
setup_logging(app_settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    logger.info("Starting up Zero Inertia API...")

    # Seed database with default data
    await seed_database()

    # Start background scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Background scheduler started")

    yield

    # Shutdown scheduler
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

    logger.info("Shutting down Zero Inertia API...")
    await engine.dispose()


app = FastAPI(
    title=app_settings.project_name,
    description="Intelligent to-do list application with AI integration",
    version="0.1.0",
    docs_url="/docs" if app_settings.environment == "development" else None,
    redoc_url="/redoc" if app_settings.environment == "development" else None,
    lifespan=lifespan,
)
# Rate limiting initialization
limiter = get_rate_limiter()
app.state.limiter = limiter

# Register custom exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# Register exception handler with monitoring
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Session middleware (for OAuth state)
app.add_middleware(SessionMiddleware, secret_key=app_settings.jwt_secret_key)

# Rate limiting middleware
app.add_middleware(SlowAPIASGIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSRF protection middleware
# Exempt auth callback and health probes
app.add_middleware(
    CSRFMiddleware,
    exempt_paths={
        "/health",
        "/csrf",  # CSRF token endpoint
        "/api/v1/auth/google/login",
        "/api/v1/auth/google/callback",
        "/docs",
        "/redoc",
        "/openapi.json",
    },
)

# Health check endpoint
@app.get("/health")
@limiter.exempt  # pyright: ignore[reportUnknownMemberType]
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Zero Inertia API is running"}

# API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(project.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(section.router, prefix="/api/v1/sections", tags=["sections"])
app.include_router(task.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(checklist.router, prefix="/api/v1/checklists", tags=["checklists"])
app.include_router(priority.router, prefix="/api/v1/priorities", tags=["priorities"])
app.include_router(streak.router, prefix="/api/v1/streaks", tags=["streaks"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["statistics"])
app.include_router(label.router, prefix="/api/v1/labels", tags=["labels"])
app.include_router(note.router, prefix="/api/v1/notes", tags=["notes"])
app.include_router(notification.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])
app.include_router(genre.router, prefix="/api/v1/media", tags=["genres"])


@app.get("/csrf")
@limiter.exempt  # pyright: ignore[reportUnknownMemberType]
async def get_csrf(request: Request):
    """Issue or return CSRF token for the client.

    - Returns JSON {"csrf_token": token}
    - Sets a matching `csrf_token` cookie if missing.
    """
    import secrets

    token = request.cookies.get("csrf_token")
    new_token_generated = False

    if not token:
        token = secrets.token_urlsafe(32)
        new_token_generated = True

    response = JSONResponse({"csrf_token": token})

    if new_token_generated:
        secure = app_settings.environment == "production"
        response.set_cookie(
            key="csrf_token",
            value=token,
            max_age=app_settings.jwt_expire_minutes * 60,
            secure=secure,
            httponly=False,
            samesite="lax",
        )

    return response


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.reload,
        log_level=app_settings.log_level,
    )
