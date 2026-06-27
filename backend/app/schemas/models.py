"""Pydantic schemas for API request/response models."""

from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class BuyRule(str, Enum):
    """Buy signal rule types."""

    PRICE_ABOVE_SMA = "price_above_sma"
    SMA_CROSSOVER = "sma_crossover"


class SellRule(str, Enum):
    """Sell signal rule types."""

    PRICE_BELOW_SMA = "price_below_sma"
    SMA_CROSSOVER = "sma_crossover"


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: str
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    """User login payload."""

    email: str
    password: str


class AuthResponse(BaseModel):
    """Authentication response with token."""

    access_token: str
    user_id: str
    email: str


class ProfileResponse(BaseModel):
    """User profile response."""

    id: str
    email: str
    created_at: str | None = None


class OHLCVBar(BaseModel):
    """Single OHLCV candle."""

    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataResponse(BaseModel):
    """Market data response for a ticker."""

    ticker: str
    timeframe: str
    data: list[OHLCVBar]


class StrategyBase(BaseModel):
    """Shared strategy fields."""

    name: str = Field(min_length=1, max_length=100)
    ticker: str = Field(min_length=1, max_length=20)
    buy_rule: BuyRule
    sell_rule: SellRule
    short_sma_period: int = Field(gt=0)
    long_sma_period: int = Field(gt=0)
    starting_cash: float = Field(gt=0)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_strategy(self) -> "StrategyBase":
        """Validate SMA periods and date range."""
        if self.long_sma_period <= self.short_sma_period:
            raise ValueError("long_sma_period must be greater than short_sma_period")
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class StrategyCreate(StrategyBase):
    """Create strategy request."""


class StrategyUpdate(StrategyBase):
    """Update strategy request."""


class StrategyResponse(StrategyBase):
    """Strategy response with metadata."""

    id: UUID
    user_id: UUID
    created_at: str
    updated_at: str


class TradeRecord(BaseModel):
    """Single trade from a backtest."""

    trade_type: str
    trade_date: str
    price: float
    shares: float
    portfolio_value: float
    pnl: float | None = None


class EquityPoint(BaseModel):
    """Point on the equity curve."""

    date: str
    value: float


class SignalMarker(BaseModel):
    """Buy/sell marker for chart display."""

    time: str
    type: str
    price: float


class BacktestRequest(BaseModel):
    """Backtest request with inline config or strategy id."""

    strategy_id: UUID | None = None
    name: str | None = None
    ticker: str | None = None
    buy_rule: BuyRule | None = None
    sell_rule: SellRule | None = None
    short_sma_period: int | None = None
    long_sma_period: int | None = None
    starting_cash: float | None = None
    start_date: date | None = None
    end_date: date | None = None


class BacktestResponse(BaseModel):
    """Full backtest results."""

    backtest_id: UUID
    ticker: str
    start_date: str
    end_date: str
    starting_cash: float
    final_portfolio_value: float
    total_return_pct: float
    num_trades: int
    win_rate: float | None
    max_drawdown_pct: float | None
    trades: list[TradeRecord]
    equity_curve: list[EquityPoint]
    ohlcv: list[OHLCVBar]
    signals: list[SignalMarker]
    config: dict[str, Any]


class BacktestSummary(BaseModel):
    """Summary of a saved backtest."""

    id: UUID
    strategy_id: UUID | None
    ticker: str
    start_date: str
    end_date: str
    starting_cash: float
    final_value: float
    total_return_pct: float
    num_trades: int
    win_rate: float | None
    max_drawdown_pct: float | None
    created_at: str
