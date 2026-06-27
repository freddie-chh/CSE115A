# BacktestLab — FXReplay-Style Backtesting MVP

A full-stack backtesting platform where users can register, view market charts, create SMA-based trading strategies, and run backtests against historical price data.

## Tech Stack

- **Frontend:** React + TypeScript + Tailwind CSS + Vite
- **Backend:** FastAPI (Python)
- **Auth / Database:** Supabase
- **Charts:** TradingView Lightweight Charts
- **Market Data:** Yahoo Finance (`yfinance`)

## Features

- User registration, login, logout with protected routes
- Interactive candlestick chart with ticker search and timeframes (1D, 1W, 1M, 3M, 1Y)
- Rule-based strategy builder (SMA crossover / price cross rules)
- Backtesting engine with equity curve, trade history, win rate, and max drawdown
- Save, edit, delete, and re-run strategies

## Project Structure

```
├── frontend/          # React app (port 5173)
├── backend/           # FastAPI app (port 8000)
├── supabase/
│   └── migrations/    # Database schema
└── .env.example       # Environment variable template
```

## Setup

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project.
2. Enable **Email** auth under Authentication → Providers.
3. Copy your **Project URL**, **anon key**, and **service role key** from Settings → API.

### 2. Apply Database Migration

Open the Supabase SQL Editor and run the contents of:

```
supabase/migrations/001_initial_schema.sql
```

This creates `profiles`, `strategies`, `backtests`, and `trades` tables with Row Level Security.

### 3. Configure Environment

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Fill in your Supabase credentials in both files:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
VITE_API_URL=http://localhost:8000
```

### 4. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs available at http://localhost:8000/docs

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at http://localhost:5173

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT |
| POST | `/auth/logout` | Logout |
| GET | `/me` | Get current user profile |
| GET | `/market-data/{ticker}` | OHLCV chart data |
| POST | `/strategies` | Create strategy |
| GET | `/strategies` | List strategies |
| GET | `/strategies/{id}` | Get strategy |
| PUT | `/strategies/{id}` | Update strategy |
| DELETE | `/strategies/{id}` | Delete strategy |
| POST | `/backtest` | Run backtest |
| GET | `/backtests/{id}` | Get backtest results |
| GET | `/backtests` | List backtests |

## Strategy Rules

**Buy signals:**
- `price_above_sma` — Price crosses above short SMA
- `sma_crossover` — Short SMA crosses above long SMA

**Sell signals:**
- `price_below_sma` — Price crosses below short SMA
- `sma_crossover` — Short SMA crosses below long SMA

Backtests simulate all-in buys and full sells at daily close prices.

## Example Tickers

`AAPL`, `TSLA`, `SPY`, `MSFT`, `BTC-USD`, `ETH-USD`
