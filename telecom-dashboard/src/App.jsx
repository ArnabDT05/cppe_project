// App.jsx — Telecom Network Analytics Dashboard
// Fetches live data from Flask API at http://127.0.0.1:5000/stats

import { useState, useEffect } from 'react'
import './App.css'
import HourlyDropChart from './HourlyDropChart'
import SignalTrendChart from './SignalTrendChart'
import SignalDistChart from './SignalDistChart'
import PredictionForm  from './PredictionForm'

// ── API endpoint ────────────────────────────────────────────────
const API_URL = 'http://127.0.0.1:5000/stats'

// ── Fallback data (shown while loading or if API is offline) ────
const FALLBACK = {
  summary: { 
    total_calls: 1000, calls_dropped: 372, calls_completed: 628, drop_pct: 37.2,
    avg_signal: -85.5, critical_calls: 120, health_index: 62.8, active_towers: 10 
  },
  minute_series:  [],
  towers:  [],
  signal_dist: { Excellent: 200, Good: 400, Fair: 280, Critical: 120 }
}

/* ── Helper components ─────────────────────────────────────── */
function LoadingCard({ text = 'Loading…' }) {
  return (
    <div className="card" style={{ textAlign: 'center', color: '#9ca3af', padding: '2.5rem' }}>
      <span style={{ fontSize: '1.3rem' }}>⏳</span>
      <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>{text}</p>
    </div>
  )
}

function ErrorBanner({ message }) {
  return (
    <div
      className="card"
      style={{
        background: '#fef2f2',
        border: '1.5px solid #fca5a5',
        color: '#b91c1c',
        fontSize: '0.875rem',
        marginBottom: '1.25rem',
      }}
    >
      ⚠️ &nbsp;<strong>API Error:</strong> {message}
      <span style={{ color: '#9ca3af', marginLeft: '0.5rem' }}>
        — Showing static fallback data
      </span>
    </div>
  )
}

/* ── Main App ───────────────────────────────────────────────── */
export default function App() {
  // Remote data state
  const [apiData,  setApiData]  = useState(null)
  const [loading,  setLoading]  = useState(true)
  const [apiError, setApiError] = useState(null)

  // ── Fetch /stats dynamically every second ──────────────────
  useEffect(() => {
    let cancelled = false

    async function fetchStats() {
      try {
        const res  = await fetch(API_URL)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        if (!cancelled) { setApiData(json); setApiError(null) }
      } catch (err) {
        if (!cancelled) {
          setApiError(err.message || 'Could not reach API')
          setApiData(FALLBACK)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    // Fetch immediately on mount
    fetchStats()
    
    // Then poll every 1 second for live updates
    const interval = setInterval(fetchStats, 1000)

    return () => { 
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  // Use API data or fallback
  const data          = apiData ?? FALLBACK
  const summary       = data.summary
  const minute_series = data.minute_series || []
  const towers        = data.towers.slice(0, 5)
  const signal_dist   = data.signal_dist || {}

  /* ── Render ─────────────────────────────────────────────── */
  return (
    <div className="app-wrapper">
      <div className="app-container">

        {/* ── Header ─────────────────────────────────────────── */}
        <header className="app-header">
          <h1>Telecom Network Analytics</h1>
          <p>Chennai Region · Live data from Flask API · Signal-based drop predictions</p>
        </header>

        {/* ── API error banner ─────────────────────────────────── */}
        {apiError && <ErrorBanner message={apiError} />}

        {/* ── Terminal Metrics Row ───────────────────────────────── */}
        {loading ? <LoadingCard text="Fetching terminal stats…" /> : (
          <div className="metrics-row">
            <div className="metric-box">
              <p className="metric-title">TOTAL CALLS</p>
              <p className="metric-val">{summary.total_calls.toLocaleString()}</p>
            </div>
            <div className="metric-box">
              <p className="metric-title">CALLS DROPPED</p>
              <p className="metric-val" style={{color: '#ef4444'}}>{summary.calls_dropped.toLocaleString()}</p>
            </div>
            <div className="metric-box">
              <p className="metric-title">NETWORK HEALTH</p>
              <p className="metric-val" style={{color: summary.health_index > 80 ? '#10b981' : '#f59e0b'}}>{summary.health_index}%</p>
            </div>
            <div className="metric-box">
              <p className="metric-title">AVG SIGNAL</p>
              <p className="metric-val">{summary.avg_signal} dBm</p>
            </div>
            <div className="metric-box">
              <p className="metric-title">CRITICAL CALLS</p>
              <p className="metric-val" style={{color: summary.critical_calls > 100 ? '#ef4444' : '#f59e0b'}}>{summary.critical_calls}</p>
            </div>
            <div className="metric-box">
              <p className="metric-title">ACTIVE TOWERS</p>
              <p className="metric-val">{summary.active_towers}</p>
            </div>
          </div>
        )}

        {/* ── Dashboard Grid ─────────────────────────────────────── */}
        <div className="dashboard-grid terminal-grid">

          {/* Graph 1: Per Minute Drop */}
          <div className="card span-2">
            <p className="card-label">⏱️ Per-Minute Call Drops</p>
            {loading ? <p style={{color:'#9ca3af', fontSize:'0.85rem'}}>Loading chart…</p> : <div className="chart-container"><HourlyDropChart dataSeries={minute_series} /></div>}
          </div>

          {/* Graph 2: Signal Heartbeat */}
          <div className="card span-2">
            <p className="card-label">📈 Avg Signal Heartbeat</p>
            {loading ? <p style={{color:'#9ca3af', fontSize:'0.85rem'}}>Loading chart…</p> : <div className="chart-container"><SignalTrendChart dataSeries={minute_series} /></div>}
          </div>

          {/* Graph 3: Signal Distribution */}
          <div className="card">
            <p className="card-label">📊 Signal Quality Distribution</p>
            {loading ? <p style={{color:'#9ca3af', fontSize:'0.85rem'}}>Loading chart…</p> : <div className="chart-container"><SignalDistChart dist={signal_dist} /></div>}
          </div>

          {/* Top Towers */}
          <div className="card">
            <p className="card-label">📡 Top At-Risk Towers</p>
            {loading ? <p style={{color:'#9ca3af', fontSize:'0.85rem'}}>Loading data…</p> : (
              <table className="tower-table">
                <thead>
                  <tr>
                    <th style={{ width: '3rem' }}>#</th>
                    <th>Tower ID</th>
                    <th>Avg Signal</th>
                    <th className="mini-bar-cell">Drop Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {towers.map((t, i) => (
                    <tr key={t.id}>
                      <td><span className="rank-badge">{i + 1}</span></td>
                      <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>{t.id}</td>
                      <td style={{ color: '#6b7280' }}>{t.avg_signal} dBm</td>
                      <td className="mini-bar-cell">
                        <div className="mini-bar-wrap">
                          <div className="mini-bar-track">
                            <div className="mini-bar-fill" style={{ width: `${t.drop_rate}%` }} />
                          </div>
                          <span className="mini-bar-pct">{t.drop_rate}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Predictor Form */}
          <div className="card span-full">
            <p className="card-label">🔮 Call Drop Predictor</p>
            <PredictionForm />
          </div>

        </div>

        {/* ── Footer ─────────────────────────────────────────── */}
        <footer className="app-footer">
          Telecom Network Analytics · API: {API_URL} · React + Vite + Chart.js
        </footer>

      </div>
    </div>
  )
}
