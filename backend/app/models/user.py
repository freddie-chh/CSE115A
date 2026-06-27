"""User claim models derived from verified Supabase JWTs."""

from pydantic import BaseModel


class UserClaims(BaseModel):
    """Authenticated user claims extracted from a verified Supabase JWT."""

    sub: str
    email: str | None = None
    role: str | None = None
