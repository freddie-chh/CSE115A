"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the FastAPI backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_jwt_secret: str = Field(
        ...,
        description="Supabase JWT secret for HS256 fallback verification",
    )
    supabase_anon_key: str | None = Field(
        default=None,
        description="Supabase anon key (reserved for Sprint 2 database access)",
    )
    environment: str = Field(default="development", description="Deployment environment")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )
    api_prefix: str = Field(default="/api/v1", description="API route prefix")
    jwks_cache_ttl_seconds: int = Field(
        default=600,
        description="JWKS cache TTL in seconds",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return parsed CORS origins from the comma-separated env value."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def supabase_issuer(self) -> str:
        """Return the expected JWT issuer for Supabase access tokens."""
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

    @property
    def supabase_jwks_url(self) -> str:
        """Return the JWKS endpoint URL for the Supabase project."""
        return f"{self.supabase_issuer}/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
