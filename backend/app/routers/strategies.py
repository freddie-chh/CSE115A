"""Strategy CRUD routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase_client
from app.schemas.models import StrategyCreate, StrategyResponse, StrategyUpdate

router = APIRouter(prefix="/strategies", tags=["strategies"])


def _to_response(row: dict) -> StrategyResponse:
    """Convert a database row to a StrategyResponse."""
    return StrategyResponse(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        ticker=row["ticker"],
        buy_rule=row["buy_rule"],
        sell_rule=row["sell_rule"],
        short_sma_period=row["short_sma_period"],
        long_sma_period=row["long_sma_period"],
        starting_cash=float(row["starting_cash"]),
        start_date=row["start_date"],
        end_date=row["end_date"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    body: StrategyCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> StrategyResponse:
    """Create a new trading strategy."""
    payload = {
        "user_id": current_user["id"],
        "name": body.name,
        "ticker": body.ticker.upper(),
        "buy_rule": body.buy_rule.value,
        "sell_rule": body.sell_rule.value,
        "short_sma_period": body.short_sma_period,
        "long_sma_period": body.long_sma_period,
        "starting_cash": body.starting_cash,
        "start_date": body.start_date.isoformat(),
        "end_date": body.end_date.isoformat(),
    }

    result = supabase.table("strategies").insert(payload).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create strategy",
        )

    return _to_response(result.data[0])


@router.get("", response_model=list[StrategyResponse])
async def list_strategies(
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> list[StrategyResponse]:
    """List all strategies for the current user."""
    result = (
        supabase.table("strategies")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return [_to_response(row) for row in (result.data or [])]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> StrategyResponse:
    """Get a single strategy by id."""
    result = (
        supabase.table("strategies")
        .select("*")
        .eq("id", str(strategy_id))
        .eq("user_id", current_user["id"])
        .single()
        .execute()
    )

    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    return _to_response(result.data)


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    body: StrategyUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> StrategyResponse:
    """Update an existing strategy."""
    payload = {
        "name": body.name,
        "ticker": body.ticker.upper(),
        "buy_rule": body.buy_rule.value,
        "sell_rule": body.sell_rule.value,
        "short_sma_period": body.short_sma_period,
        "long_sma_period": body.long_sma_period,
        "starting_cash": body.starting_cash,
        "start_date": body.start_date.isoformat(),
        "end_date": body.end_date.isoformat(),
    }

    result = (
        supabase.table("strategies")
        .update(payload)
        .eq("id", str(strategy_id))
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    return _to_response(result.data[0])


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> None:
    """Delete a strategy."""
    result = (
        supabase.table("strategies")
        .delete()
        .eq("id", str(strategy_id))
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
