import { useState, type FormEvent } from 'react'
import type { BuyRule, SellRule, Strategy, StrategyFormData } from '../lib/types'

interface StrategyFormProps {
  initial?: Strategy
  onSubmit: (data: StrategyFormData) => Promise<void>
  onRunBacktest?: (data: StrategyFormData) => Promise<void>
  submitLabel?: string
}

const defaultValues: StrategyFormData = {
  name: '',
  ticker: 'AAPL',
  buy_rule: 'sma_crossover',
  sell_rule: 'sma_crossover',
  short_sma_period: 10,
  long_sma_period: 50,
  starting_cash: 10000,
  start_date: '2023-01-01',
  end_date: '2024-01-01',
}

export default function StrategyForm({
  initial,
  onSubmit,
  onRunBacktest,
  submitLabel = 'Save Strategy',
}: StrategyFormProps) {
  const [form, setForm] = useState<StrategyFormData>(
    initial
      ? {
          name: initial.name,
          ticker: initial.ticker,
          buy_rule: initial.buy_rule,
          sell_rule: initial.sell_rule,
          short_sma_period: initial.short_sma_period,
          long_sma_period: initial.long_sma_period,
          starting_cash: initial.starting_cash,
          start_date: initial.start_date,
          end_date: initial.end_date,
        }
      : defaultValues,
  )
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field: keyof StrategyFormData, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: FormEvent, runBacktest = false) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (runBacktest && onRunBacktest) {
        await onRunBacktest(form)
      } else {
        await onSubmit(form)
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Something went wrong'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="space-y-5">
      {error && (
        <div className="rounded-md bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Strategy Name</label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => update('name', e.target.value)}
            required
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Ticker</label>
          <input
            type="text"
            value={form.ticker}
            onChange={(e) => update('ticker', e.target.value.toUpperCase())}
            required
            placeholder="AAPL, BTC-USD"
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Buy Rule</label>
          <select
            value={form.buy_rule}
            onChange={(e) => update('buy_rule', e.target.value as BuyRule)}
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="price_above_sma">Price crosses above SMA</option>
            <option value="sma_crossover">SMA short crosses above SMA long</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Sell Rule</label>
          <select
            value={form.sell_rule}
            onChange={(e) => update('sell_rule', e.target.value as SellRule)}
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="price_below_sma">Price crosses below SMA</option>
            <option value="sma_crossover">SMA short crosses below SMA long</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Short SMA Period</label>
          <input
            type="number"
            min={1}
            value={form.short_sma_period}
            onChange={(e) => update('short_sma_period', Number(e.target.value))}
            required
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Long SMA Period</label>
          <input
            type="number"
            min={2}
            value={form.long_sma_period}
            onChange={(e) => update('long_sma_period', Number(e.target.value))}
            required
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Starting Cash ($)</label>
          <input
            type="number"
            min={1}
            step={100}
            value={form.starting_cash}
            onChange={(e) => update('starting_cash', Number(e.target.value))}
            required
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Start Date</label>
          <input
            type="date"
            value={form.start_date}
            onChange={(e) => update('start_date', e.target.value)}
            required
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">End Date</label>
          <input
            type="date"
            value={form.end_date}
            onChange={(e) => update('end_date', e.target.value)}
            required
            className="w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="flex gap-3">
        <button
          type="button"
          disabled={loading}
          onClick={(e) => handleSubmit(e, false)}
          className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
        >
          {loading ? 'Saving...' : submitLabel}
        </button>
        {onRunBacktest && (
          <button
            type="button"
            disabled={loading}
            onClick={(e) => handleSubmit(e, true)}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Backtest'}
          </button>
        )}
      </div>
    </form>
  )
}
