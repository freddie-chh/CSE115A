"""Pytest configuration and shared fixtures."""

import os
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test env vars before importing the app (config is cached via lru_cache).
os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret-for-hs256-fallback")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None, None, None]:
    """Clear the settings cache before each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_token_payload() -> dict[str, str]:
    """Return a sample verified JWT payload."""
    return {
        "sub": "user-123",
        "email": "user@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "https://test-project.supabase.co/auth/v1",
    }


@pytest.fixture
def mock_verify_token(valid_token_payload: dict[str, str]) -> Generator[AsyncMock, None, None]:
    """Patch token verification to return a valid payload without network calls."""
    with patch(
        "app.dependencies.auth.verify_supabase_token",
        new_callable=AsyncMock,
        return_value=valid_token_payload,
    ) as mock:
        yield mock
