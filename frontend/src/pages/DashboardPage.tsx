import { useCallback, useEffect, useState } from 'react'
import { marketApi } from '../lib/api'
import type { OHLCVBar, Timeframe } from '../lib/types'
import CandlestickChart from '../components/CandlestickChart'

const TIMEFRAMES: Timeframe[] = ['1D', '1W', '1M', '3M', '1Y']

export default function DashboardPage() {
  const [ticker, setTicker] = useState('AAPL')
  const [inputTicker, setInputTicker] = useState('AAPL')
  const [timeframe, setTimeframe] = useState<Timeframe>('1M')
  const [data, setData] = useState<OHLCVBar[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchData = useCallback(async (sym: string, tf: Timeframe) => {
    setLoading(true)
    setError('')
    try {
      const { data: res } = await marketApi.getData(sym, tf)
      setData(res.data)
    } catch {
      setError(`Could not load data for "${sym}". Check the ticker symbol.`)
      setData([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData(ticker, timeframe)
  }, [ticker, timeframe, fetchData])

  const handleTickerSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const sym = inputTicker.trim().toUpperCase()
    if (sym) setTicker(sym)
  }

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Market Dashboard</h1>
          <p className="text-sm text-slate-400">View live price charts for any ticker</p>
        </div>

        <form onSubmit={handleTickerSubmit} className="flex gap-2">
          <input
            type="text"
            value={inputTicker}
            onChange={(e) => setInputTicker(e.target.value.toUpperCase())}
            placeholder="AAPL, TSLA, BTC-USD"
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
          <button
            type="submit"
            className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
          >
            Load
          </button>
        </form>
      </div>

      <div className="mb-4 flex gap-2">
        {TIMEFRAMES.map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
              timeframe === tf
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {tf}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex h-96 items-center justify-center text-slate-400">
          Loading chart data...
        </div>
      )}

      {error && !loading && (
        <div className="rounded-md bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div>
          <h2 className="mb-2 text-lg font-semibold text-white">{ticker}</h2>
          <CandlestickChart data={data} height={450} />
        </div>
      )}
    </div>
  )
}
