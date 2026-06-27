"""Backtest API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase_client
from app.schemas.models import BacktestRequest, BacktestResponse, BacktestSummary
from app.services.backtest_engine import BacktestResult, StrategyConfig, run_backtest

router = APIRouter(tags=["backtest"])


def _build_config_from_request(
    body: BacktestRequest,
    strategy_row: dict | None = None,
) -> StrategyConfig:
    """Build a StrategyConfig from request body and optional saved strategy."""
    if strategy_row:
        return StrategyConfig(
            name=strategy_row["name"],
            ticker=strategy_row["ticker"],
            buy_rule=strategy_row["buy_rule"],
            sell_rule=strategy_row["sell_rule"],
            short_sma_period=strategy_row["short_sma_period"],
            long_sma_period=strategy_row["long_sma_period"],
            starting_cash=float(strategy_row["starting_cash"]),
            start_date=strategy_row["start_date"],
            end_date=strategy_row["end_date"],
        )

    required = [
        "name", "ticker", "buy_rule", "sell_rule",
        "short_sma_period", "long_sma_period", "starting_cash",
        "start_date", "end_date",
    ]
    missing = [f for f in required if getattr(body, f) is None]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing)}",
        )

    return StrategyConfig(
        name=body.name or "Unnamed Strategy",
        ticker=body.ticker.upper(),  # type: ignore[union-attr]
        buy_rule=body.buy_rule.value if body.buy_rule else "",  # type: ignore[union-attr]
        sell_rule=body.sell_rule.value if body.sell_rule else "",  # type: ignore[union-attr]
        short_sma_period=body.short_sma_period,  # type: ignore[arg-type]
        long_sma_period=body.long_sma_period,  # type: ignore[arg-type]
        starting_cash=body.starting_cash,  # type: ignore[arg-type]
        start_date=body.start_date.isoformat(),  # type: ignore[union-attr]
        end_date=body.end_date.isoformat(),  # type: ignore[union-attr]
    )


def _result_to_response(
    result: BacktestResult, backtest_id: UUID, strategy_id: UUID | None
) -> BacktestResponse:
    """Convert engine result to API response."""
    return BacktestResponse(
        backtest_id=backtest_id,
        ticker=result.config["ticker"],
        start_date=result.config["start_date"],
        end_date=result.config["end_date"],
        starting_cash=result.config["starting_cash"],
        final_portfolio_value=result.final_portfolio_value,
        total_return_pct=result.total_return_pct,
        num_trades=result.num_trades,
        win_rate=result.win_rate,
        max_drawdown_pct=result.max_drawdown_pct,
        trades=result.trades,
        equity_curve=result.equity_curve,
        ohlcv=result.ohlcv,
        signals=result.signals,
        config=result.config,
    )


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest_endpoint(
    body: BacktestRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> BacktestResponse:
    """Run a backtest and persist results."""
    strategy_row: dict | None = None
    strategy_id = body.strategy_id

    if strategy_id:
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
        strategy_row = result.data

    config = _build_config_from_request(body, strategy_row)

    if config.long_sma_period <= config.short_sma_period:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="long_sma_period must be greater than short_sma_period",
        )

    try:
        bt_result = run_backtest(config)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    backtest_payload = {
        "user_id": current_user["id"],
        "strategy_id": str(strategy_id) if strategy_id else None,
        "ticker": config.ticker,
        "start_date": config.start_date,
        "end_date": config.end_date,
        "starting_cash": config.starting_cash,
        "final_value": bt_result.final_portfolio_value,
        "total_return_pct": bt_result.total_return_pct,
        "num_trades": bt_result.num_trades,
        "win_rate": bt_result.win_rate,
        "max_drawdown_pct": bt_result.max_drawdown_pct,
        "config": {
            **bt_result.config,
            "signals": [s.model_dump() for s in bt_result.signals],
            "ohlcv": [b.model_dump() for b in bt_result.ohlcv],
        },
        "equity_curve": [p.model_dump() for p in bt_result.equity_curve],
    }

    saved = supabase.table("backtests").insert(backtest_payload).execute()
    if not saved.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save backtest",
        )

    backtest_id = saved.data[0]["id"]

    if bt_result.trades:
        trade_rows = [
            {
                "backtest_id": backtest_id,
                "trade_type": t.trade_type,
                "trade_date": t.trade_date,
                "price": t.price,
                "shares": t.shares,
                "portfolio_value": t.portfolio_value,
                "pnl": t.pnl,
            }
            for t in bt_result.trades
        ]
        supabase.table("trades").insert(trade_rows).execute()

    return _result_to_response(bt_result, UUID(backtest_id), strategy_id)


@router.get("/backtests/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> BacktestResponse:
    """Retrieve a saved backtest with full results."""
    result = (
        supabase.table("backtests")
        .select("*")
        .eq("id", str(backtest_id))
        .eq("user_id", current_user["id"])
        .single()
        .execute()
    )

    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )

    row = result.data
    trades_result = (
        supabase.table("trades")
        .select("*")
        .eq("backtest_id", str(backtest_id))
        .order("trade_date")
        .execute()
    )

    from app.schemas.models import TradeRecord, EquityPoint

    trades = [
        TradeRecord(
            trade_type=t["trade_type"],
            trade_date=t["trade_date"],
            price=float(t["price"]),
            shares=float(t["shares"]),
            portfolio_value=float(t["portfolio_value"]),
            pnl=float(t["pnl"]) if t["pnl"] is not None else None,
        )
        for t in (trades_result.data or [])
    ]

    equity_curve = [
        EquityPoint(date=p["date"], value=float(p["value"]))
        for p in (row.get("equity_curve") or [])
    ]

    config = row["config"]
    from app.schemas.models import OHLCVBar, SignalMarker

    ohlcv = [
        OHLCVBar(**b) for b in (config.get("ohlcv") or [])
    ]
    signals = [
        SignalMarker(**s) for s in (config.get("signals") or [])
    ]

    if not ohlcv:
        try:
            rerun = run_backtest(
                StrategyConfig(
                    name=config["name"],
                    ticker=config["ticker"],
                    buy_rule=config["buy_rule"],
                    sell_rule=config["sell_rule"],
                    short_sma_period=config["short_sma_period"],
                    long_sma_period=config["long_sma_period"],
                    starting_cash=float(config["starting_cash"]),
                    start_date=config["start_date"],
                    end_date=config["end_date"],
                )
            )
            ohlcv = rerun.ohlcv
            signals = rerun.signals
        except ValueError:
            ohlcv = []
            signals = []

    return BacktestResponse(
        backtest_id=UUID(row["id"]),
        ticker=row["ticker"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        starting_cash=float(row["starting_cash"]),
        final_portfolio_value=float(row["final_value"]),
        total_return_pct=float(row["total_return_pct"]),
        num_trades=row["num_trades"],
        win_rate=float(row["win_rate"]) if row["win_rate"] is not None else None,
        max_drawdown_pct=float(row["max_drawdown_pct"]) if row["max_drawdown_pct"] is not None else None,
        trades=trades,
        equity_curve=equity_curve,
        ohlcv=ohlcv,
        signals=signals,
        config=config,
    )


@router.get("/backtests", response_model=list[BacktestSummary])
async def list_backtests(
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase_client)],
) -> list[BacktestSummary]:
    """List all backtests for the current user."""
    result = (
        supabase.table("backtests")
        .select("id, strategy_id, ticker, start_date, end_date, starting_cash, final_value, total_return_pct, num_trades, win_rate, max_drawdown_pct, created_at")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .execute()
    )

    return [
        BacktestSummary(
            id=row["id"],
            strategy_id=row.get("strategy_id"),
            ticker=row["ticker"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            starting_cash=float(row["starting_cash"]),
            final_value=float(row["final_value"]),
            total_return_pct=float(row["total_return_pct"]),
            num_trades=row["num_trades"],
            win_rate=float(row["win_rate"]) if row["win_rate"] is not None else None,
            max_drawdown_pct=float(row["max_drawdown_pct"]) if row["max_drawdown_pct"] is not None else None,
            created_at=row["created_at"],
        )
        for row in (result.data or [])
    ]
