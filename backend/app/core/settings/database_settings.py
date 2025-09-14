from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    database_name: str = Field(alias="DB_NAME")
    user: str = Field(alias="DB_USER")
    password: str = Field(alias="DB_PASSWORD")
    driver: str = Field(default="postgresql+asyncpg", alias="DB_DRIVER")


    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def connection_url(self) -> str:
        """Build database connection URL"""
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"
