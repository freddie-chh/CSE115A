"""Backtesting engine for SMA-based strategies."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.schemas.models import (
    EquityPoint,
    OHLCVBar,
    SignalMarker,
    TradeRecord,
)
from app.services.market_data import fetch_historical_daily


@dataclass
class StrategyConfig:
    """Configuration for a backtest run."""

    name: str
    ticker: str
    buy_rule: str
    sell_rule: str
    short_sma_period: int
    long_sma_period: int
    starting_cash: float
    start_date: str
    end_date: str


@dataclass
class BacktestResult:
    """Results from a backtest simulation."""

    final_portfolio_value: float
    total_return_pct: float
    num_trades: int
    win_rate: float | None
    max_drawdown_pct: float | None
    trades: list[TradeRecord]
    equity_curve: list[EquityPoint]
    ohlcv: list[OHLCVBar]
    signals: list[SignalMarker]
    config: dict


def _compute_sma(series: pd.Series, period: int) -> pd.Series:
    """Compute simple moving average."""
    return series.rolling(window=period, min_periods=period).mean()


def _generate_signals(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
    """Add buy/sell signal columns to the dataframe."""
    df = df.copy()
    df["sma_short"] = _compute_sma(df["close"], config.short_sma_period)
    df["sma_long"] = _compute_sma(df["close"], config.long_sma_period)

    df["buy_signal"] = False
    df["sell_signal"] = False

    for i in range(1, len(df)):
        if pd.isna(df["sma_short"].iloc[i]) or pd.isna(df["sma_long"].iloc[i]):
            continue

        prev_close = df["close"].iloc[i - 1]
        curr_close = df["close"].iloc[i]
        prev_short = df["sma_short"].iloc[i - 1]
        curr_short = df["sma_short"].iloc[i]
        prev_long = df["sma_long"].iloc[i - 1]
        curr_long = df["sma_long"].iloc[i]

        if config.buy_rule == "price_above_sma":
            if prev_close <= prev_short and curr_close > curr_short:
                df.iloc[i, df.columns.get_loc("buy_signal")] = True
        elif config.buy_rule == "sma_crossover":
            if prev_short <= prev_long and curr_short > curr_long:
                df.iloc[i, df.columns.get_loc("buy_signal")] = True

        if config.sell_rule == "price_below_sma":
            if prev_close >= prev_short and curr_close < curr_short:
                df.iloc[i, df.columns.get_loc("sell_signal")] = True
        elif config.sell_rule == "sma_crossover":
            if prev_short >= prev_long and curr_short < curr_long:
                df.iloc[i, df.columns.get_loc("sell_signal")] = True

    return df


def _simulate_trades(df: pd.DataFrame, starting_cash: float) -> tuple[
    list[TradeRecord], list[EquityPoint], list[SignalMarker], float | None, int, float
]:
    """Simulate all-in buys and full sells based on signals."""
    cash = starting_cash
    shares = 0.0
    trades: list[TradeRecord] = []
    equity_curve: list[EquityPoint] = []
    signals: list[SignalMarker] = []
    round_trip_pnls: list[float] = []
    entry_price = 0.0

    for _, row in df.iterrows():
        date_str = row["time"]
        price = float(row["close"])
        portfolio_value = cash + shares * price
        equity_curve.append(EquityPoint(date=date_str, value=round(portfolio_value, 2)))

        if row["buy_signal"] and shares == 0 and cash > 0:
            shares = cash / price
            cash = 0.0
            entry_price = price
            trades.append(
                TradeRecord(
                    trade_type="buy",
                    trade_date=date_str,
                    price=round(price, 4),
                    shares=round(shares, 4),
                    portfolio_value=round(shares * price, 2),
                    pnl=None,
                )
            )
            signals.append(SignalMarker(time=date_str, type="buy", price=round(price, 4)))

        elif row["sell_signal"] and shares > 0:
            proceeds = shares * price
            pnl = proceeds - (entry_price * shares)
            round_trip_pnls.append(pnl)
            cash = proceeds
            trades.append(
                TradeRecord(
                    trade_type="sell",
                    trade_date=date_str,
                    price=round(price, 4),
                    shares=round(shares, 4),
                    portfolio_value=round(cash, 2),
                    pnl=round(pnl, 2),
                )
            )
            signals.append(SignalMarker(time=date_str, type="sell", price=round(price, 4)))
            shares = 0.0
            entry_price = 0.0

    final_value = cash + shares * float(df["close"].iloc[-1])
    num_trades = len(trades)

    win_rate: float | None = None
    if round_trip_pnls:
        wins = sum(1 for p in round_trip_pnls if p > 0)
        win_rate = round((wins / len(round_trip_pnls)) * 100, 2)

    return trades, equity_curve, signals, win_rate, num_trades, final_value


def _compute_max_drawdown(equity_curve: list[EquityPoint]) -> float | None:
    """Compute maximum drawdown percentage from equity curve."""
    if len(equity_curve) < 2:
        return None

    values = np.array([p.value for p in equity_curve])
    peak = values[0]
    max_dd = 0.0

    for value in values:
        if value > peak:
            peak = value
        dd = (peak - value) / peak * 100 if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd

    return round(max_dd, 2)


def run_backtest(config: StrategyConfig) -> BacktestResult:
    """Run a full backtest for the given strategy configuration."""
    bars = fetch_historical_daily(config.ticker, config.start_date, config.end_date)

    if len(bars) < config.long_sma_period + 1:
        raise ValueError(
            f"Insufficient data: need at least {config.long_sma_period + 1} bars, "
            f"got {len(bars)}"
        )

    df = pd.DataFrame(
        {
            "time": [b.time for b in bars],
            "open": [b.open for b in bars],
            "high": [b.high for b in bars],
            "low": [b.low for b in bars],
            "close": [b.close for b in bars],
            "volume": [b.volume for b in bars],
        }
    )

    df = _generate_signals(df, config)
    trades, equity_curve, signals, win_rate, num_trades, final_value = _simulate_trades(
        df, config.starting_cash
    )

    total_return_pct = round(
        ((final_value - config.starting_cash) / config.starting_cash) * 100, 2
    )
    max_drawdown_pct = _compute_max_drawdown(equity_curve)

    config_dict = {
        "name": config.name,
        "ticker": config.ticker,
        "buy_rule": config.buy_rule,
        "sell_rule": config.sell_rule,
        "short_sma_period": config.short_sma_period,
        "long_sma_period": config.long_sma_period,
        "starting_cash": config.starting_cash,
        "start_date": config.start_date,
        "end_date": config.end_date,
    }

    return BacktestResult(
        final_portfolio_value=round(final_value, 2),
        total_return_pct=total_return_pct,
        num_trades=num_trades,
        win_rate=win_rate,
        max_drawdown_pct=max_drawdown_pct,
        trades=trades,
        equity_curve=equity_curve,
        ohlcv=bars,
        signals=signals,
        config=config_dict,
    )
