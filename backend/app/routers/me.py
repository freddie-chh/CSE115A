"""Authenticated user profile endpoint."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import UserClaims

router = APIRouter(tags=["auth"])


@router.get("/me")
async def get_me(current_user: UserClaims = Depends(get_current_user)) -> dict[str, str | None]:
    """Return the authenticated user's claims from their verified JWT."""
    return {
        "id": current_user.sub,
        "email": current_user.email,
        "role": current_user.role,
    }
