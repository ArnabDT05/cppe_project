// App.jsx — Telecom Network Analytics Dashboard
// Fetches live data from Flask API at http://127.0.0.1:5000/stats

import { useState, useEffect } from 'react'
import './App.css'
import HourlyDropChart from './HourlyDropChart'
import PredictionForm  from './PredictionForm'

// ── API endpoint ────────────────────────────────────────────────
const API_URL = 'http://127.0.0.1:5000/stats'

// ── Fallback data (shown while loading or if API is offline) ────
const FALLBACK = {
  summary: { total_calls: 1000, calls_dropped: 372, calls_completed: 628, drop_pct: 37.2 },
  hourly:  Array.from({ length: 24 }, (_, h) => ({ hour: h, drops: 0, drop_rate: 0 })),
  towers:  [],
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

  // ── Fetch /stats on mount ────────────────────────────────────
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

    fetchStats()
    return () => { cancelled = true }
  }, [])

  // Use API data or fallback
  const data    = apiData ?? FALLBACK
  const summary = data.summary
  const hourly  = data.hourly
  const towers  = data.towers.slice(0, 5)

  /* ── Render ─────────────────────────────────────────────── */
  return (
    <div className="app-wrapper">
      <div className="app-container">

        {/* ── Header ─────────────────────────────────────────── */}
        <header className="app-header">
          <h1>📡 Telecom Network Analytics</h1>
          <p>Chennai Region · Live data from Flask API · Signal-based drop prediction</p>
        </header>

        {/* ── API error banner ─────────────────────────────────── */}
        {apiError && <ErrorBanner message={apiError} />}

        {/* ── Section 1: KPI cards ─────────────────────────────── */}
        {loading ? <LoadingCard text="Fetching stats from API…" /> : (
          <div className="kpi-row">
            <div className="kpi-card">
              <span className="kpi-card-label">Total Calls</span>
              <span className="kpi-card-value">{summary.total_calls.toLocaleString()}</span>
              <span className="kpi-card-sub">All records</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-card-label">Calls Dropped</span>
              <span className="kpi-card-value color-red">{summary.calls_dropped.toLocaleString()}</span>
              <span className="kpi-card-sub">signal &lt; −95 dBm</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-card-label">Calls Completed</span>
              <span className="kpi-card-value color-green">{summary.calls_completed.toLocaleString()}</span>
              <span className="kpi-card-sub">signal ≥ −95 dBm</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-card-label">Drop Rate</span>
              <span className="kpi-card-value">{summary.drop_pct}%</span>
              <span className="kpi-card-sub">of all calls</span>
            </div>
          </div>
        )}

        {/* ── Section 2: Hourly line chart ─────────────────────── */}
        <div className="card">
          <p className="card-label">🕐 Hourly Call Drop Distribution</p>
          {loading
            ? <p style={{ color: '#9ca3af', fontSize: '0.85rem' }}>Loading chart…</p>
            : <div className="chart-container"><HourlyDropChart hourly={hourly} /></div>
          }
        </div>

        {/* ── Section 3: Top towers table ──────────────────────── */}
        <div className="card">
          <p className="card-label">🗼 Top 5 Towers — Highest Drop Rate</p>
          {loading ? (
            <p style={{ color: '#9ca3af', fontSize: '0.85rem' }}>Loading towers…</p>
          ) : towers.length === 0 ? (
            <p style={{ color: '#9ca3af', fontSize: '0.85rem' }}>No tower data available.</p>
          ) : (
            <table className="tower-table">
              <thead>
                <tr>
                  <th style={{ width: '3rem' }}>#</th>
                  <th>Tower ID</th>
                  <th>Avg Signal</th>
                  <th>Total Calls</th>
                  <th className="mini-bar-cell">Drop Rate</th>
                </tr>
              </thead>
              <tbody>
                {towers.map((t, i) => (
                  <tr key={t.id}>
                    <td><span className="rank-badge">{i + 1}</span></td>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>{t.id}</td>
                    <td style={{ color: '#6b7280' }}>{t.avg_signal} dBm</td>
                    <td style={{ color: '#6b7280' }}>{t.total_calls}</td>
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

        {/* ── Section 4: Prediction form ───────────────────────── */}
        <div className="card">
          <p className="card-label">🔮 Call Drop Predictor</p>
          <PredictionForm />
        </div>

        {/* ── Footer ─────────────────────────────────────────── */}
        <footer className="app-footer">
          Telecom Network Analytics · API: {API_URL} · React + Vite + Chart.js
        </footer>

      </div>
    </div>
  )
}
