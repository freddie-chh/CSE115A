import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import StrategyForm from '../components/StrategyForm'
import { backtestApi, strategyApi } from '../lib/api'
import type { Strategy, StrategyFormData } from '../lib/types'

export default function EditStrategyPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [strategy, setStrategy] = useState<Strategy | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    strategyApi
      .get(id)
      .then(({ data }) => setStrategy(data))
      .catch(() => navigate('/strategies'))
      .finally(() => setLoading(false))
  }, [id, navigate])

  const handleSubmit = async (data: StrategyFormData) => {
    if (!id) return
    await strategyApi.update(id, data)
    navigate('/strategies')
  }

  const handleRunBacktest = async (data: StrategyFormData) => {
    if (!id) return
    await strategyApi.update(id, data)
    const { data: result } = await backtestApi.run({ strategy_id: id })
    navigate(`/backtests/${result.backtest_id}`)
  }

  if (loading) return <div className="text-slate-400">Loading...</div>
  if (!strategy) return null

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Edit Strategy</h1>
      <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
        <StrategyForm
          initial={strategy}
          onSubmit={handleSubmit}
          onRunBacktest={handleRunBacktest}
          submitLabel="Update Strategy"
        />
      </div>
    </div>
  )
}
