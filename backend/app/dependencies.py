"""FastAPI dependencies for authentication."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from app.config import Settings, get_settings

security = HTTPBearer()


def get_supabase_client(settings: Annotated[Settings, Depends(get_settings)]) -> Client:
    """Create a Supabase client with the anon key."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase_admin(settings: Annotated[Settings, Depends(get_settings)]) -> Client:
    """Create a Supabase client with the service role key."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> dict:
    """Validate JWT and return the authenticated user."""
    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return {"id": response.user.id, "email": response.user.email, "token": token}
