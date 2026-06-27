import type { TradeRecord } from '../lib/types'

interface TradeTableProps {
  trades: TradeRecord[]
}

export default function TradeTable({ trades }: TradeTableProps) {
  if (trades.length === 0) {
    return (
      <p className="text-center text-slate-400 py-8">No trades executed during this backtest.</p>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700">
      <table className="w-full text-sm">
        <thead className="bg-slate-800 text-slate-300">
          <tr>
            <th className="px-4 py-3 text-left">Date</th>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-right">Price</th>
            <th className="px-4 py-3 text-right">Shares</th>
            <th className="px-4 py-3 text-right">Portfolio</th>
            <th className="px-4 py-3 text-right">P&L</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {trades.map((trade, i) => (
            <tr key={i} className="hover:bg-slate-800/50">
              <td className="px-4 py-2 text-slate-300">{trade.trade_date}</td>
              <td className="px-4 py-2">
                <span
                  className={`rounded px-2 py-0.5 text-xs font-medium ${
                    trade.trade_type === 'buy'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {trade.trade_type.toUpperCase()}
                </span>
              </td>
              <td className="px-4 py-2 text-right text-slate-300">
                ${trade.price.toFixed(2)}
              </td>
              <td className="px-4 py-2 text-right text-slate-300">
                {trade.shares.toFixed(4)}
              </td>
              <td className="px-4 py-2 text-right text-slate-300">
                ${trade.portfolio_value.toFixed(2)}
              </td>
              <td className="px-4 py-2 text-right">
                {trade.pnl !== null ? (
                  <span className={trade.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </span>
                ) : (
                  <span className="text-slate-500">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
