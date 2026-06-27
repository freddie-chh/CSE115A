import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { backtestApi, strategyApi } from '../lib/api'
import type { Strategy } from '../lib/types'

export default function StrategiesPage() {
  const navigate = useNavigate()
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [runningId, setRunningId] = useState<string | null>(null)

  const loadStrategies = async () => {
    try {
      const { data } = await strategyApi.list()
      setStrategies(data)
    } catch {
      setStrategies([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStrategies()
  }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this strategy?')) return
    await strategyApi.delete(id)
    setStrategies((prev) => prev.filter((s) => s.id !== id))
  }

  const handleRun = async (id: string) => {
    setRunningId(id)
    try {
      const { data } = await backtestApi.run({ strategy_id: id })
      navigate(`/backtests/${data.backtest_id}`)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Backtest failed'
      alert(typeof msg === 'string' ? msg : 'Backtest failed')
    } finally {
      setRunningId(null)
    }
  }

  if (loading) {
    return <div className="text-slate-400">Loading strategies...</div>
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Saved Strategies</h1>
          <p className="text-sm text-slate-400">Create and manage your trading strategies</p>
        </div>
        <Link
          to="/strategies/new"
          className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
        >
          New Strategy
        </Link>
      </div>

      {strategies.length === 0 ? (
        <div className="rounded-lg border border-slate-700 bg-slate-800 p-12 text-center">
          <p className="text-slate-400">No strategies yet.</p>
          <Link
            to="/strategies/new"
            className="mt-2 inline-block text-emerald-400 hover:underline"
          >
            Create your first strategy
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-700">
          <table className="w-full text-sm">
            <thead className="bg-slate-800 text-slate-300">
              <tr>
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">Ticker</th>
                <th className="px-4 py-3 text-left">Buy Rule</th>
                <th className="px-4 py-3 text-left">Sell Rule</th>
                <th className="px-4 py-3 text-right">SMA</th>
                <th className="px-4 py-3 text-right">Cash</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {strategies.map((s) => (
                <tr key={s.id} className="hover:bg-slate-800/50">
                  <td className="px-4 py-3 font-medium text-white">{s.name}</td>
                  <td className="px-4 py-3 text-slate-300">{s.ticker}</td>
                  <td className="px-4 py-3 text-slate-400">{s.buy_rule.replace(/_/g, ' ')}</td>
                  <td className="px-4 py-3 text-slate-400">{s.sell_rule.replace(/_/g, ' ')}</td>
                  <td className="px-4 py-3 text-right text-slate-300">
                    {s.short_sma_period}/{s.long_sma_period}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-300">
                    ${s.starting_cash.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => handleRun(s.id)}
                        disabled={runningId === s.id}
                        className="rounded bg-blue-600 px-2 py-1 text-xs text-white hover:bg-blue-500 disabled:opacity-50"
                      >
                        {runningId === s.id ? 'Running...' : 'Run'}
                      </button>
                      <Link
                        to={`/strategies/${s.id}/edit`}
                        className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-200 hover:bg-slate-600"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDelete(s.id)}
                        className="rounded bg-red-600/20 px-2 py-1 text-xs text-red-400 hover:bg-red-600/30"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
