"""Market data service using Yahoo Finance."""

import logging
from datetime import datetime

import yfinance as yf

from app.schemas.models import OHLCVBar

logger = logging.getLogger(__name__)

TIMEFRAME_MAP: dict[str, dict[str, str]] = {
    "1D": {"period": "1d", "interval": "5m"},
    "1W": {"period": "5d", "interval": "15m"},
    "1M": {"period": "1mo", "interval": "1d"},
    "3M": {"period": "3mo", "interval": "1d"},
    "1Y": {"period": "1y", "interval": "1d"},
}


def _format_time(ts: datetime, interval: str) -> str:
    """Format timestamp for chart consumption."""
    if interval in ("5m", "15m", "30m", "1h"):
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    return ts.strftime("%Y-%m-%d")


def fetch_market_data(ticker: str, timeframe: str = "1M") -> list[OHLCVBar]:
    """Fetch OHLCV data from Yahoo Finance for a ticker and timeframe."""
    params = TIMEFRAME_MAP.get(timeframe, TIMEFRAME_MAP["1M"])
    interval = params["interval"]

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=params["period"], interval=interval)
    except Exception as exc:
        logger.error("Failed to fetch market data for %s: %s", ticker, exc)
        raise ValueError(f"Failed to fetch data for ticker '{ticker}'") from exc

    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}'")

    bars: list[OHLCVBar] = []
    for ts, row in df.iterrows():
        bars.append(
            OHLCVBar(
                time=_format_time(ts.to_pydatetime(), interval),
                open=round(float(row["Open"]), 4),
                high=round(float(row["High"]), 4),
                low=round(float(row["Low"]), 4),
                close=round(float(row["Close"]), 4),
                volume=round(float(row["Volume"]), 2),
            )
        )

    return bars


def fetch_historical_daily(ticker: str, start_date: str, end_date: str) -> list[OHLCVBar]:
    """Fetch daily OHLCV data for a date range (used by backtesting)."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, interval="1d")
    except Exception as exc:
        logger.error("Failed to fetch historical data for %s: %s", ticker, exc)
        raise ValueError(f"Failed to fetch historical data for '{ticker}'") from exc

    if df.empty:
        raise ValueError(
            f"No historical data for '{ticker}' between {start_date} and {end_date}"
        )

    bars: list[OHLCVBar] = []
    for ts, row in df.iterrows():
        bars.append(
            OHLCVBar(
                time=ts.strftime("%Y-%m-%d"),
                open=round(float(row["Open"]), 4),
                high=round(float(row["High"]), 4),
                low=round(float(row["Low"]), 4),
                close=round(float(row["Close"]), 4),
                volume=round(float(row["Volume"]), 2),
            )
        )

    return bars
