// HourlyDropChart.jsx
// --------------------
// Reusable line chart component for hourly call drop distribution.
// Props:
//   hourly — array of { hour: number, drops: number } from the API

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

// Register required Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

export default function HourlyDropChart({ hourly = [] }) {
  // ── Derived values ──────────────────────────────────────────
  const labels     = hourly.map(r => `${String(r.hour).padStart(2, '0')}:00`)
  const dropCounts = hourly.map(r => r.drops)
  const maxDrops   = Math.max(...dropCounts, 1)
  const peakIdx    = dropCounts.indexOf(maxDrops)

  // Point colours — highlight the peak hour in red, rest dark grey
  const pointColors = dropCounts.map((_, i) =>
    i === peakIdx ? '#dc2626' : '#374151'
  )
  const pointSizes = dropCounts.map((_, i) =>
    i === peakIdx ? 6 : 3
  )

  // ── Chart.js data ───────────────────────────────────────────
  const data = {
    labels,
    datasets: [
      {
        label: 'Call Drops',
        data: dropCounts,

        // Line
        borderColor: '#374151',
        borderWidth: 2,

        // Fill area under line
        fill: true,
        backgroundColor: 'rgba(55, 65, 81, 0.07)',

        // Points
        pointBackgroundColor: pointColors,
        pointBorderColor:     pointColors,
        pointBorderWidth:     1.5,
        pointRadius:          pointSizes,
        pointHoverRadius:     7,
        pointHoverBackgroundColor: '#dc2626',
        pointHoverBorderColor:     '#fff',
        pointHoverBorderWidth:     2,

        // Smooth curve
        tension: 0.38,
      },
    ],
  }

  // ── Chart.js options ────────────────────────────────────────
  const options = {
    responsive: true,
    maintainAspectRatio: true,   // chart scales with container width

    interaction: {
      mode: 'index',             // tooltip shows value for the hovered x position
      intersect: false,
    },

    plugins: {
      // Hide legend — label is in card-label above the chart
      legend: { display: false },

      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#f9fafb',
        bodyColor:  '#d1d5db',
        padding:    10,
        cornerRadius: 6,
        displayColors: false,
        callbacks: {
          // Custom tooltip title: "16:00 — Peak Hour" for the busiest slot
          title: ([item]) => {
            const suffix = item.dataIndex === peakIdx ? '  ★ Peak Hour' : ''
            return `${item.label}${suffix}`
          },
          // Custom body: "26 drops"
          label: item => ` ${item.parsed.y} drops`,
        },
      },
    },

    scales: {
      x: {
        title: {
          display: true,
          text: 'Hour of Day',
          color: '#9ca3af',
          font: { size: 11, weight: '500' },
          padding: { top: 6 },
        },
        ticks: {
          color: '#9ca3af',
          font: { size: 10 },
          maxRotation: 45,
          autoSkip: false,   // show all 24 hour labels
        },
        grid: { color: '#f3f4f6' },
      },

      y: {
        title: {
          display: true,
          text: 'Call Drops',
          color: '#9ca3af',
          font: { size: 11, weight: '500' },
          padding: { bottom: 6 },
        },
        ticks: {
          color: '#9ca3af',
          font: { size: 10 },
          precision: 0,        // integers only
        },
        grid: { color: '#f3f4f6' },
        beginAtZero: true,
        suggestedMax: maxDrops + 3,   // small breathing room above peak
      },
    },
  }

  // ── Render ──────────────────────────────────────────────────
  if (hourly.length === 0) {
    return (
      <p style={{ color: '#9ca3af', fontSize: '0.85rem', padding: '1rem 0' }}>
        No hourly data available.
      </p>
    )
  }

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <Line id="hourly-drop-chart" data={data} options={options} />

      {/* Peak hour annotation below chart */}
      {peakIdx >= 0 && (
        <p style={{
          marginTop: '0.75rem',
          fontSize: '0.75rem',
          color: '#9ca3af',
          textAlign: 'right',
        }}>
          ★ Peak hour: <strong style={{ color: '#dc2626' }}>
            {labels[peakIdx]} — {maxDrops} drops
          </strong>
        </p>
      )}
    </div>
  )
}
