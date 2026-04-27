// PredictionForm.jsx
// -------------------
// Standalone form that POSTs to http://127.0.0.1:5000/predict and
// displays "Call Drop Likely" or "No Drop Expected" below the button.

import { useState } from 'react'
import './PredictionForm.css'

const PREDICT_URL = 'http://127.0.0.1:5000/predict'

export default function PredictionForm() {
  // ── Field values ────────────────────────────────────────────
  const [signal,  setSignal]  = useState('-100')   // string so input stays controlled
  const [hour,    setHour]    = useState('18')

  // ── UI state ────────────────────────────────────────────────
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)   // API response object | null
  const [apiErr,  setApiErr]  = useState(null)   // network / server error string

  // ── Per-field validation errors ─────────────────────────────
  const [signalErr, setSignalErr] = useState('')
  const [hourErr,   setHourErr]   = useState('')

  // ── Validate fields; return true if all OK ───────────────────
  function validate() {
    let ok = true

    const sig = parseFloat(signal)
    if (isNaN(sig) || sig < -130 || sig > -30) {
      setSignalErr('Enter a value between −130 and −30 dBm')
      ok = false
    } else {
      setSignalErr('')
    }

    const hr = parseInt(hour, 10)
    if (isNaN(hr) || hr < 0 || hr > 23) {
      setHourErr('Enter a whole number between 0 and 23')
      ok = false
    } else {
      setHourErr('')
    }

    return ok
  }

  // ── Call POST /predict ───────────────────────────────────────
  async function handlePredict() {
    if (!validate()) return

    setLoading(true)
    setResult(null)
    setApiErr(null)

    try {
      const res = await fetch(PREDICT_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          signal_strength: parseFloat(signal),
          time_hour:       parseInt(hour, 10),
        }),
      })

      const json = await res.json()

      if (!res.ok) {
        // Server returned a 4xx / 5xx with an error message
        setApiErr(json.error || `Server error (${res.status})`)
      } else {
        setResult(json)
      }
    } catch (err) {
      setApiErr('Could not reach the API. Is the Flask server running?')
    } finally {
      setLoading(false)
    }
  }

  // ── Determine result card style ──────────────────────────────
  const resultClass = result
    ? result.call_drop === 1 ? 'pf-result pf-result--drop' : 'pf-result pf-result--ok'
    : apiErr ? 'pf-result pf-result--err' : ''

  // ── Render ───────────────────────────────────────────────────
  return (
    <div>
      <div className="pf-grid">

        {/* Signal strength input */}
        <div className="pf-group" id="signal-group">
          <label htmlFor="signal-input" className="pf-label">
            Signal Strength (dBm)
          </label>
          <p className="pf-hint">Typical range: −110 to −70 dBm</p>
          <input
            id="signal-input"
            type="number"
            className={`pf-input ${result?.call_drop === 1 ? 'pf-input--drop' : result?.call_drop === 0 ? 'pf-input--ok' : ''}`}
            value={signal}
            min={-130}
            max={-30}
            step={1}
            placeholder="-100"
            onChange={e => { setSignal(e.target.value); setResult(null); setSignalErr('') }}
          />
          {signalErr && <span className="pf-field-error">{signalErr}</span>}
        </div>

        {/* Hour of day input */}
        <div className="pf-group" id="hour-group">
          <label htmlFor="hour-input" className="pf-label">
            Hour of Day (0 – 23)
          </label>
          <p className="pf-hint">Peak hours: 08, 16, 20, 21</p>
          <input
            id="hour-input"
            type="number"
            className={`pf-input ${result?.call_drop === 1 ? 'pf-input--drop' : result?.call_drop === 0 ? 'pf-input--ok' : ''}`}
            value={hour}
            min={0}
            max={23}
            step={1}
            placeholder="18"
            onChange={e => { setHour(e.target.value); setResult(null); setHourErr('') }}
          />
          {hourErr && <span className="pf-field-error">{hourErr}</span>}
        </div>
      </div>

      {/* Predict button */}
      <button
        id="predict-btn"
        className="pf-btn"
        onClick={handlePredict}
        disabled={loading}
      >
        {loading && <span className="pf-spinner" />}
        {loading ? 'Predicting…' : 'Predict Call Drop'}
      </button>

      {/* ── Result (API success) ─────────────────────────────── */}
      {result && (
        <div className={resultClass} role="alert">
          <span className="pf-result-icon">
            {result.call_drop === 1 ? '⚠️' : '✅'}
          </span>
          <div className="pf-result-body">
            <div className="pf-result-verdict">{result.result}</div>
            <div className="pf-result-meta">
              Signal: {result.signal_strength} dBm
              &nbsp;·&nbsp;
              Hour: {String(result.time_hour).padStart(2, '0')}:00
              &nbsp;·&nbsp;
              Confidence: {result.confidence}%
            </div>
            <div className="pf-conf-track">
              <div className="pf-conf-fill" style={{ width: `${result.confidence}%` }} />
            </div>
          </div>
        </div>
      )}

      {/* ── API / network error ──────────────────────────────── */}
      {apiErr && !result && (
        <div className="pf-result pf-result--err" role="alert">
          <span className="pf-result-icon">⚡</span>
          <div className="pf-result-body">
            <div className="pf-result-verdict">API Error</div>
            <div className="pf-result-meta">{apiErr}</div>
          </div>
        </div>
      )}
    </div>
  )
}
