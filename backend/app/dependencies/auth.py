"""Supabase JWT verification dependencies for protected API routes."""

import logging
import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt

from app.config import Settings, get_settings
from app.models.user import UserClaims

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

_jwks_cache: dict[str, Any] | None = None
_jwks_cache_expires_at: float = 0.0


async def _fetch_jwks(settings: Settings) -> dict[str, Any]:
    """Fetch JWKS from Supabase with in-memory TTL caching."""
    global _jwks_cache, _jwks_cache_expires_at

    now = time.time()
    if _jwks_cache is not None and now < _jwks_cache_expires_at:
        return _jwks_cache

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.supabase_jwks_url)
            response.raise_for_status()
            jwks_data = response.json()
    except httpx.HTTPError as exc:
        logger.error("Failed to fetch JWKS from Supabase: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc

    _jwks_cache = jwks_data
    _jwks_cache_expires_at = now + settings.jwks_cache_ttl_seconds
    return jwks_data


def _get_signing_key(kid: str, jwks_data: dict[str, Any]) -> Any:
    """Return the JWK matching the token key ID."""
    keys = jwks_data.get("keys", [])
    for key in keys:
        if key.get("kid") == kid:
            return jwk.construct(key)
    raise JWTError(f"No matching JWK found for kid: {kid}")


def _decode_with_jwks(token: str, jwks_data: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Decode and verify a JWT using JWKS public keys."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    if not kid:
        raise JWTError("Token missing key ID (kid) in header")

    signing_key = _get_signing_key(kid, jwks_data)
    algorithms = list({key.get("alg") for key in jwks_data.get("keys", []) if key.get("alg")})
    if not algorithms:
        algorithms = ["ES256", "RS256"]

    return jwt.decode(
        token,
        signing_key,
        algorithms=algorithms,
        audience="authenticated",
        issuer=settings.supabase_issuer,
        options={"verify_aud": True, "verify_iss": True, "verify_exp": True},
    )


def _decode_with_secret(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and verify a JWT using the Supabase HS256 JWT secret."""
    return jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        audience="authenticated",
        issuer=settings.supabase_issuer,
        options={"verify_aud": True, "verify_iss": True, "verify_exp": True},
    )


async def verify_supabase_token(token: str, settings: Settings) -> dict[str, Any]:
    """Verify a Supabase access token using JWKS with HS256 fallback."""
    jwks_data = await _fetch_jwks(settings)
    keys = jwks_data.get("keys", [])

    if keys:
        try:
            return _decode_with_jwks(token, jwks_data, settings)
        except JWTError as exc:
            logger.warning("JWKS verification failed, no HS256 fallback attempted: %s", exc)
            raise

    if not settings.supabase_jwt_secret:
        raise JWTError("No JWKS keys available and no JWT secret configured")

    return _decode_with_secret(token, settings)


def _build_user_claims(payload: dict[str, Any]) -> UserClaims:
    """Map a verified JWT payload to UserClaims."""
    sub = payload.get("sub")
    if not sub:
        raise JWTError("Token missing subject (sub) claim")

    return UserClaims(
        sub=sub,
        email=payload.get("email"),
        role=payload.get("role"),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    settings: Settings = Depends(get_settings),
) -> UserClaims:
    """FastAPI dependency that validates a Supabase JWT and returns user claims."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = await verify_supabase_token(credentials.credentials, settings)
        return _build_user_claims(payload)
    except JWTError as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
