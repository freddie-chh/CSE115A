import { useEffect, useRef } from 'react'
import {
  createChart,
  ColorType,
  CandlestickSeries,
  createSeriesMarkers,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type Time,
  type SeriesMarker,
} from 'lightweight-charts'
import type { OHLCVBar, SignalMarker } from '../lib/types'

interface CandlestickChartProps {
  data: OHLCVBar[]
  signals?: SignalMarker[]
  height?: number
}

function toChartTime(time: string): Time {
  if (time.includes(' ')) {
    return Math.floor(new Date(time.replace(' ', 'T')).getTime() / 1000) as Time
  }
  return time as Time
}

export default function CandlestickChart({
  data,
  signals = [],
  height = 400,
}: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const markersRef = useRef<ReturnType<typeof createSeriesMarkers<Time>> | null>(null)

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

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    chartRef.current = chart
    seriesRef.current = series
    markersRef.current = createSeriesMarkers(series, [])

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
      chartRef.current = null
      seriesRef.current = null
      markersRef.current = null
    }
  }, [height])

  useEffect(() => {
    if (!seriesRef.current || data.length === 0) return

    const candleData: CandlestickData[] = data.map((bar) => ({
      time: toChartTime(bar.time),
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
    }))

    seriesRef.current.setData(candleData)

    const markers: SeriesMarker<Time>[] = signals.map((s) => ({
      time: toChartTime(s.time),
      position: s.type === 'buy' ? 'belowBar' : 'aboveBar',
      color: s.type === 'buy' ? '#22c55e' : '#ef4444',
      shape: s.type === 'buy' ? 'arrowUp' : 'arrowDown',
      text: s.type.toUpperCase(),
    }))

    markersRef.current?.setMarkers(markers)
    chartRef.current?.timeScale().fitContent()
  }, [data, signals])

  return (
    <div
      ref={containerRef}
      className="w-full overflow-hidden rounded-lg border border-slate-700"
    />
  )
}
