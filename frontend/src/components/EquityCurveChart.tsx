import { useEffect, useRef } from 'react'
import {
  createChart,
  ColorType,
  LineSeries,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type Time,
} from 'lightweight-charts'
import type { EquityPoint } from '../lib/types'

interface EquityCurveChartProps {
  data: EquityPoint[]
  height?: number
}

export default function EquityCurveChart({ data, height = 250 }: EquityCurveChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Line'> | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1e293b' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#334155' },
        horzLines: { color: '#334155' },
      },
      width: containerRef.current.clientWidth,
      height,
    })

    const series = chart.addSeries(LineSeries, {
      color: '#3b82f6',
      lineWidth: 2,
    })

    chartRef.current = chart
    seriesRef.current = series

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [height])

  useEffect(() => {
    if (!seriesRef.current || data.length === 0) return

    const lineData: LineData[] = data.map((p) => ({
      time: p.date as Time,
      value: p.value,
    }))

    seriesRef.current.setData(lineData)
    chartRef.current?.timeScale().fitContent()
  }, [data])

  return (
    <div
      ref={containerRef}
      className="w-full overflow-hidden rounded-lg border border-slate-700"
    />
  )
}
