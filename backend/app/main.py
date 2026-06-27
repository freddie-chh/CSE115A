"""FXReplay Backtesting API."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase_client
from app.schemas.models import ProfileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, backtest, market_data, strategies

settings = get_settings()

app = FastAPI(
    title="FXReplay Backtesting API",
    description="Backtesting platform for rule-based trading strategies",
    version="0.1.0",
)

origins = [o.strip() for o in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(market_data.router)
app.include_router(strategies.router)
app.include_router(backtest.router)


@app.get("/me", response_model=ProfileResponse)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return ProfileResponse(
        id=result.data["id"],
        email=result.data["email"],
        created_at=result.data.get("created_at"),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
