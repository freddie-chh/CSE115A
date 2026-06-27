export type BuyRule = 'price_above_sma' | 'sma_crossover'
export type SellRule = 'price_below_sma' | 'sma_crossover'

export interface OHLCVBar {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface Strategy {
  id: string
  user_id: string
  name: string
  ticker: string
  buy_rule: BuyRule
  sell_rule: SellRule
  short_sma_period: number
  long_sma_period: number
  starting_cash: number
  start_date: string
  end_date: string
  created_at: string
  updated_at: string
}

export interface StrategyFormData {
  name: string
  ticker: string
  buy_rule: BuyRule
  sell_rule: SellRule
  short_sma_period: number
  long_sma_period: number
  starting_cash: number
  start_date: string
  end_date: string
}

export interface TradeRecord {
  trade_type: 'buy' | 'sell'
  trade_date: string
  price: number
  shares: number
  portfolio_value: number
  pnl: number | null
}

export interface EquityPoint {
  date: string
  value: number
}

export interface SignalMarker {
  time: string
  type: 'buy' | 'sell'
  price: number
}

export interface BacktestResult {
  backtest_id: string
  ticker: string
  start_date: string
  end_date: string
  starting_cash: number
  final_portfolio_value: number
  total_return_pct: number
  num_trades: number
  win_rate: number | null
  max_drawdown_pct: number | null
  trades: TradeRecord[]
  equity_curve: EquityPoint[]
  ohlcv: OHLCVBar[]
  signals: SignalMarker[]
  config: Record<string, unknown>
}

export interface AuthResponse {
  access_token: string
  user_id: string
  email: string
}

export interface Profile {
  id: string
  email: string
  created_at?: string
}

export type Timeframe = '1D' | '1W' | '1M' | '3M' | '1Y'
