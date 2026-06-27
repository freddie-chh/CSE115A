import { useNavigate } from 'react-router-dom'
import StrategyForm from '../components/StrategyForm'
import { backtestApi, strategyApi } from '../lib/api'
import type { StrategyFormData } from '../lib/types'

export default function NewStrategyPage() {
  const navigate = useNavigate()

  const handleSubmit = async (data: StrategyFormData) => {
    await strategyApi.create(data)
    navigate('/strategies')
  }

  const handleRunBacktest = async (data: StrategyFormData) => {
    const { data: strategy } = await strategyApi.create(data)
    const { data: result } = await backtestApi.run({ strategy_id: strategy.id })
    navigate(`/backtests/${result.backtest_id}`)
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">New Strategy</h1>
      <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
        <StrategyForm
          onSubmit={handleSubmit}
          onRunBacktest={handleRunBacktest}
          submitLabel="Save Strategy"
        />
      </div>
    </div>
  )
}
