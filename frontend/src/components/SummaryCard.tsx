interface SummaryCardProps {
  label: string
  value: string
  positive?: boolean | null
}

export default function SummaryCard({ label, value, positive }: SummaryCardProps) {
  let valueColor = 'text-white'
  if (positive === true) valueColor = 'text-emerald-400'
  if (positive === false) valueColor = 'text-red-400'

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${valueColor}`}>{value}</p>
    </div>
  )
}
