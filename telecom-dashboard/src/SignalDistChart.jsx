// SignalDistChart.jsx
import {
  Chart as ChartJS,
  CategoryScale, LinearScale,
  BarElement, Tooltip
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

export default function SignalDistChart({ dist = {} }) {
  const labels = ["Excellent", "Good", "Fair", "Critical"]
  const dataValues = labels.map(l => dist[l] || 0)
  
  // Colors: Excellent(Green), Good(Blue), Fair(Yellow), Critical(Red)
  const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']

  const data = {
    labels,
    datasets: [{
      data: dataValues,
      backgroundColor: colors,
      borderRadius: 4,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    animation: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1f2937',
        displayColors: true,
        callbacks: {
          label: item => ` ${item.parsed.y} calls`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af', font: { size: 10 } },
        grid: { display: false }
      },
      y: {
        ticks: { color: '#9ca3af', font: { size: 10 }, precision: 0 },
        grid: { color: '#f3f4f6' },
        beginAtZero: true
      }
    }
  }

  return <Bar data={data} options={options} />
}
