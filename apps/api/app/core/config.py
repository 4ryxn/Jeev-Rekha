from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_DATABASE_URL = "postgresql+psycopg://jeevrekha:jeevrekha@localhost:5432/jeevrekha"
LOCAL_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
LOCAL_TRUSTED_HOSTS = "localhost,127.0.0.1,testserver"


class Settings(BaseSettings):
    """Application settings loaded from the environment or a local .env file."""

    app_name: str = "Jeev Rekha API"
    app_env: Literal["development", "test", "production"] = "development"
    cors_origins: str = LOCAL_CORS_ORIGINS
    trusted_hosts: str = LOCAL_TRUSTED_HOSTS
    database_url: str | None = None
    routing_provider_base_url: str | None = "https://router.project-osrm.org"
    demo_seed_enabled: bool | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        """Keep local setup simple while rejecting unsafe production defaults."""
        if not self.database_url:
            if self.app_env == "production":
                raise ValueError("DATABASE_URL is required when APP_ENV=production")
            self.database_url = LOCAL_DATABASE_URL

        if self.demo_seed_enabled is None:
            self.demo_seed_enabled = self.app_env != "production"

        if self.app_env == "production":
            if not self.cors_origin_list or "*" in self.cors_origin_list:
                raise ValueError("CORS_ORIGINS must be an explicit non-wildcard allowlist in production")
            if not self.trusted_host_list or "*" in self.trusted_host_list:
                raise ValueError("TRUSTED_HOSTS must be an explicit non-wildcard allowlist in production")
            if self.demo_seed_enabled:
                raise ValueError("DEMO_SEED_ENABLED must be false in production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_host_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
