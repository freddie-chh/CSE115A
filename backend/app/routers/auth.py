"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase_admin, get_supabase_client
from app.schemas.models import AuthResponse, LoginRequest, ProfileResponse, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register(
    body: RegisterRequest,
    supabase: Annotated[Client, Depends(get_supabase_client)],
    supabase_admin: Annotated[Client, Depends(get_supabase_admin)],
) -> AuthResponse:
    """Register a new user via Supabase Auth."""
    try:
        auth_response = supabase.auth.sign_up(
            {"email": body.email, "password": body.password}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email may already be in use.",
        )

    # Ensure profile exists (trigger should handle this, but upsert as fallback)
    supabase_admin.table("profiles").upsert(
        {"id": auth_response.user.id, "email": body.email}
    ).execute()

    return AuthResponse(
        access_token=auth_response.session.access_token,
        user_id=auth_response.user.id,
        email=body.email,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> AuthResponse:
    """Log in an existing user."""
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return AuthResponse(
        access_token=auth_response.session.access_token,
        user_id=auth_response.user.id,
        email=auth_response.user.email or body.email,
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> dict[str, str]:
    """Sign out the current user."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=ProfileResponse)
async def get_me(
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> ProfileResponse:
    """Return the authenticated user's profile."""
    result = (
        supabase.table("profiles")
        .select("id, email, created_at")
        .eq("id", current_user["id"])
        .single()
        .execute()
    )

    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return ProfileResponse(
        id=result.data["id"],
        email=result.data["email"],
        created_at=result.data.get("created_at"),
    )
