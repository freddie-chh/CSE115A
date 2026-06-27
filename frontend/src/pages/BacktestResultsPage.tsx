import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { backtestApi } from '../lib/api'
import type { BacktestResult } from '../lib/types'
import SummaryCard from '../components/SummaryCard'
import CandlestickChart from '../components/CandlestickChart'
import EquityCurveChart from '../components/EquityCurveChart'
import TradeTable from '../components/TradeTable'

export default function BacktestResultsPage() {
  const { id } = useParams<{ id: string }>()
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    backtestApi
      .get(id)
      .then(({ data }) => setResult(data))
      .catch(() => setError('Failed to load backtest results'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return <div className="text-slate-400">Loading results...</div>
  }

  if (error || !result) {
    return (
      <div className="rounded-md bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
        {error || 'Results not found'}
      </div>
    )
  }

  const isPositive = result.total_return_pct >= 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Backtest Results</h1>
        <p className="text-sm text-slate-400">
          {result.ticker} &middot; {result.start_date} to {result.end_date}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <SummaryCard
          label="Final Value"
          value={`$${result.final_portfolio_value.toLocaleString()}`}
          positive={isPositive}
        />
        <SummaryCard
          label="Total Return"
          value={`${isPositive ? '+' : ''}${result.total_return_pct.toFixed(2)}%`}
          positive={isPositive}
        />
        <SummaryCard label="Trades" value={String(result.num_trades)} />
        <SummaryCard
          label="Win Rate"
          value={result.win_rate !== null ? `${result.win_rate.toFixed(1)}%` : 'N/A'}
          positive={result.win_rate !== null ? result.win_rate >= 50 : null}
        />
        <SummaryCard
          label="Max Drawdown"
          value={
            result.max_drawdown_pct !== null
              ? `${result.max_drawdown_pct.toFixed(2)}%`
              : 'N/A'
          }
          positive={false}
        />
      </div>

      <div>
        <h2 className="mb-2 text-lg font-semibold text-white">
          Price Chart with Signals
        </h2>
        <CandlestickChart
          data={result.ohlcv}
          signals={result.signals}
          height={400}
        />
      </div>

      <div>
        <h2 className="mb-2 text-lg font-semibold text-white">Equity Curve</h2>
        <EquityCurveChart data={result.equity_curve} height={250} />
      </div>

      <div>
        <h2 className="mb-2 text-lg font-semibold text-white">Trade History</h2>
        <TradeTable trades={result.trades} />
      </div>
    </div>
  )
}
