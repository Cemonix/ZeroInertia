import sys
from pathlib import Path

from loguru import logger

from app.core.settings.app_settings import AppSettings


def setup_logging(settings: AppSettings) -> None:
    """Configure loguru logging for the application."""
    # Remove default handler
    logger.remove()

    # Console logging with colors
    log_level = "DEBUG" if settings.debug else "INFO"
    _ = logger.add(
        sys.stderr,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " +
               "<level>{level}</level> | " +
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " +
               "<level>{message}</level>",
        level=log_level,
    )

    # File logging (only in non-development environments)
    if settings.environment != "development":
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # General application logs
        _ = logger.add(
            logs_dir / "app.log",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        )

        # Error logs
        _ = logger.add(
            logs_dir / "errors.log",
            rotation="10 MB",
            retention="60 days",
            compression="zip",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        )

    logger.info(f"Logging configured for {settings.environment} environment")


# Export logger for use throughout the app
__all__ = ["logger", "setup_logging"]
