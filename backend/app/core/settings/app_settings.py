from enum import StrEnum
from typing import ClassVar

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_app_settings_instance: "AppSettings | None" = None

class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    project_name: str = Field(default="Zero Inertia", alias="PROJECT_NAME")
    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")
    environment: Environment = Field(default=Environment.DEVELOPMENT, alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    # CORS Configuration
    backend_cors_origins: str = Field(default="http://localhost:5173", alias="BACKEND_CORS_ORIGINS")

    # AI Service Configuration
    ai_api_key: str = Field(default="", alias="AI_API_KEY")

    # Monitoring / metrics
    metrics_api_key: str | None = Field(default=None, alias="METRICS_API_KEY")

    # OAuth Configuration
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    oauth_redirect_uri: str = Field(default="http://localhost:8000/api/v1/auth/google/callback", alias="OAUTH_REDIRECT_URI")

    # JWT Configuration
    jwt_secret_key: str = Field(default="", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, alias="JWT_EXPIRE_MINUTES")  # 24 hours

    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    # Firebase Push Notifications
    firebase_service_account_path: str = Field(default="", alias="FIREBASE_SERVICE_ACCOUNT_PATH")

    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    reload: bool = Field(default=True, alias="RELOAD")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    # Rate limiting (process-local by default)
    rate_limit_anon_per_min: int = Field(default=60, alias="RATE_LIMIT_ANON_PER_MIN")
    rate_limit_auth_per_min: int = Field(default=120, alias="RATE_LIMIT_AUTH_PER_MIN")
    rate_limit_burst_multiplier: float = Field(default=1.0, alias="RATE_LIMIT_BURST_MULTIPLIER")
    rate_limit_exempt_paths_csv: str = Field(
        default="/health,/csrf,/docs,/redoc,/openapi.json",
        alias="RATE_LIMIT_EXEMPT_PATHS",
    )
    rate_limit_storage_uri: str = Field(
        default="",
        alias="RATE_LIMIT_STORAGE_URI",
        description="Optional SlowAPI storage URI (e.g., redis://:pass@host:6379/0). Empty uses in-memory.",
    )

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_settings(self) -> "AppSettings":
        """Validate settings after initialization."""
        if self.environment not in {"development", "production", "testing"}:
            raise ValueError("ENVIRONMENT must be one of 'development', 'production', or 'testing'.")

        if self.environment == "production" and self.debug:
            raise ValueError("DEBUG must be False in production environment.")

        if not self.cors_origins:
            raise ValueError("CORS_ORIGINS must be provided.")

        if self.jwt_secret_key == "" or len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for security.")

        if self.google_client_id == "" or self.google_client_secret == "":
            raise ValueError("Google OAuth credentials must be provided.")

        if self.ai_api_key == "":
            raise ValueError("AI_API_KEY must be provided.")

        if self.redis_password == "":
            raise ValueError("REDIS_PASSWORD must be provided for secure Redis connection.")

        return self

    @property
    def cors_origins(self) -> list[str]:
        """Convert comma-separated CORS origins to list."""
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def rate_limit_exempt_paths(self) -> set[str]:
        return {p.strip() for p in self.rate_limit_exempt_paths_csv.split(',') if p.strip()}


def get_app_settings() -> AppSettings:
    """Get the singleton instance of AppSettings."""
    global _app_settings_instance
    if _app_settings_instance is None:
        _app_settings_instance = AppSettings()
    return _app_settings_instance
