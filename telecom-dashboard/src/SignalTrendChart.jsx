// SignalTrendChart.jsx
import {
  Chart as ChartJS,
  CategoryScale, LinearScale,
  PointElement, LineElement, Tooltip, Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler)

export default function SignalTrendChart({ dataSeries = [] }) {
  const labels = dataSeries.map(r => r.minute)
  const signals = dataSeries.map(r => r.avg_signal)
  
  const data = {
    labels,
    datasets: [{
      label: 'Avg Signal',
      data: signals,
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 4,
      fill: true,
      tension: 0.4,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    animation: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#f9fafb',
        bodyColor: '#d1d5db',
        displayColors: false,
        callbacks: {
          label: item => ` ${item.parsed.y} dBm`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af', font: { size: 10 } },
        grid: { display: false }
      },
      y: {
        title: { display: true, text: 'dBm', color: '#9ca3af', font: { size: 10 } },
        ticks: { color: '#9ca3af', font: { size: 10 } },
        grid: { color: '#f3f4f6' },
        min: -110,
        max: -60
      }
    }
  }

  if (dataSeries.length === 0) return <p style={{color:'#9ca3af', fontSize:'0.85rem'}}>No data...</p>

  return <Line data={data} options={options} />
}
