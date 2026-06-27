"""Market data API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user
from app.schemas.models import MarketDataResponse
from app.services.market_data import TIMEFRAME_MAP, fetch_market_data

router = APIRouter(tags=["market-data"])


@router.get("/market-data/{ticker}", response_model=MarketDataResponse)
async def get_market_data(
    ticker: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    timeframe: str = Query(default="1M"),
) -> MarketDataResponse:
    """Return OHLCV market data for a ticker."""
    if timeframe not in TIMEFRAME_MAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timeframe. Choose from: {', '.join(TIMEFRAME_MAP)}",
        )

    try:
        data = fetch_market_data(ticker.upper(), timeframe)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return MarketDataResponse(ticker=ticker.upper(), timeframe=timeframe, data=data)
