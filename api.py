"""
api.py
------
Flask REST API for the Telecom Call Drop Analytics dashboard.

Endpoints
---------
  GET  /stats    →  summary, hourly distribution, top towers
  POST /predict  →  { signal_strength, time_hour } → call drop prediction
  GET  /health   →  liveness check

Run with:  python3 api.py
Server   : http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import joblib
import os
import threading
import time
import random

app = Flask(__name__)
CORS(app)   # allow requests from the React dev server (localhost:5173)

DATA_FILE = "telecom_data.csv"
MODEL_FILE = "rf_model.pkl"

# ── Load initial data into memory for live simulation ──────────
if os.path.exists(DATA_FILE):
    live_df = pd.read_csv(DATA_FILE)
    # Override historical timestamps to span the last 60 minutes for demo
    now = pd.Timestamp.now()
    times = [now - pd.Timedelta(seconds=int(i * 3600 / len(live_df))) for i in range(len(live_df))]
    times.reverse()
    live_df["timestamp"] = [t.strftime("%Y-%m-%d %H:%M:%S") for t in times]
else:
    live_df = pd.DataFrame(columns=["call_id", "timestamp", "latitude", "longitude", "tower_id", "signal_strength", "time_hour", "call_drop"])

TOWER_IDS = [f"TOWER_{str(i).zfill(4)}" for i in range(1, 11)]

# Track infinitely growing calls separately from the 5000-row memory buffer
total_simulated_calls = len(live_df)
total_dropped_calls = int(live_df["call_drop"].sum()) if not live_df.empty else 0

def generate_live_data():
    """Background thread that adds new synthetic calls every second."""
    global live_df, total_simulated_calls, total_dropped_calls
    while True:
        time.sleep(1)
        
        # Generate 1 to 5 new calls per second
        new_calls = []
        for _ in range(random.randint(1, 5)):
            signal = round(random.uniform(-110, -50), 2)
            call_drop = 1 if signal < -95 else 0
            hour = random.randint(0, 23)
            
            new_calls.append({
                "call_id": f"CALL_LIVE_{random.randint(10000, 99999)}",
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": round(random.uniform(12.8, 13.2), 4),
                "longitude": round(random.uniform(80.1, 80.3), 4),
                "tower_id": random.choice(TOWER_IDS),
                "signal_strength": signal,
                "time_hour": hour,
                "call_drop": call_drop
            })
            
            # Increment global counters for the dashboard
            total_simulated_calls += 1
            total_dropped_calls += call_drop
            
        new_df = pd.DataFrame(new_calls)
        live_df = pd.concat([live_df, new_df], ignore_index=True)
        
        # Keep only the last 5000 rows in memory to prevent memory leak
        if len(live_df) > 5000:
            live_df = live_df.tail(5000)

# Load ML model once at startup
if os.path.exists(MODEL_FILE):
    rf_model = joblib.load(MODEL_FILE)
else:
    rf_model = None


def load_stats():
    """Compute all analytics from the live in-memory dataframe and return as a dict."""
    global live_df, total_simulated_calls, total_dropped_calls
    df = live_df.copy()

    total = len(df)
    if total == 0:
        return {"summary": {}, "minute_series": [], "towers": []}
    
    # Calculate extra terminal metrics based on the current 5000-row window
    drops_in_window = int(df["call_drop"].sum())
    drop_rate_pct = (total_dropped_calls / total_simulated_calls * 100) if total_simulated_calls > 0 else 0
    avg_network_signal = round(df["signal_strength"].mean(), 1)
    critical_calls = int((df["signal_strength"] < -100).sum())
    health_index = round(100 - drop_rate_pct, 1)
    active_towers = int(df["tower_id"].nunique())

    # ── Minute-by-minute distribution (Last 30 mins) ─────────
    df["ts"] = pd.to_datetime(df["timestamp"])
    df["minute"] = df["ts"].dt.strftime("%H:%M")
    
    minute_series = (
        df.groupby("minute")
        .agg(
            total_calls=("call_drop", "count"),
            drops=("call_drop", "sum"),
            avg_signal=("signal_strength", "mean")
        )
        .assign(drop_rate=lambda x: (x["drops"] / x["total_calls"] * 100).round(1))
        .assign(avg_signal=lambda x: x["avg_signal"].round(1))
        .reset_index()
        .tail(30)  # show last 30 minutes on the graph
    )

    # ── Top 10 towers by drop count ──────────────────────────
    towers = (
        df.groupby("tower_id")
        .agg(
            total_calls=("call_drop", "count"),
            drops=("call_drop", "sum"),
            avg_signal=("signal_strength", "mean"),
        )
        .assign(drop_rate=lambda x: (x["drops"] / x["total_calls"] * 100).round(1))
        .assign(avg_signal=lambda x: x["avg_signal"].round(2))
        .sort_values("drops", ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"tower_id": "id"})
    )

    # ── Signal Distribution Buckets ──────────────────────────
    bins = [-float("inf"), -95, -85, -70, float("inf")]
    labels = ["Critical", "Fair", "Good", "Excellent"]
    df["signal_quality"] = pd.cut(df["signal_strength"], bins=bins, labels=labels)
    dist = df["signal_quality"].value_counts().reindex(labels).fillna(0).to_dict()

    return {
        "summary": {
            "total_calls":  total_simulated_calls,
            "calls_dropped": total_dropped_calls,
            "calls_completed": total_simulated_calls - total_dropped_calls,
            "drop_pct": round(drop_rate_pct, 1),
            "avg_signal": avg_network_signal,
            "critical_calls": critical_calls,
            "health_index": health_index,
            "active_towers": active_towers
        },
        "minute_series":  minute_series.to_dict(orient="records"),
        "towers":  towers.to_dict(orient="records"),
        "signal_dist": dist
    }


@app.route("/stats", methods=["GET"])
def stats():
    """Return full analytics payload as JSON."""
    try:
        data = load_stats()
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": f"'{DATA_FILE}' not found. Run generate_data.py first."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict whether a call will drop based on signal strength and hour.

    Request body (JSON)
    -------------------
    {
      "signal_strength": float,   # dBm, e.g. -100
      "time_hour":       int      # 0–23
    }

    Response (JSON)
    ---------------
    {
      "call_drop":    0 or 1,
      "result":       "Call Drop Likely" | "No Drop Expected",
      "confidence":   float (0–100 %),
      "signal_strength": float,
      "time_hour":    int
    }
    """
    body = request.get_json(silent=True) or {}

    # ── Validate inputs ──────────────────────────────────────
    try:
        signal = float(body["signal_strength"])
        hour   = int(body["time_hour"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "Provide 'signal_strength' (float) and 'time_hour' (int 0–23)."
        }), 400

    if not (-130 <= signal <= -30):
        return jsonify({"error": "signal_strength must be between -130 and -30 dBm."}), 400
    if not (0 <= hour <= 23):
        return jsonify({"error": "time_hour must be between 0 and 23."}), 400

    if rf_model is None:
        return jsonify({"error": "Random Forest model not found. Please run model.py first."}), 500

    # ── Inference via Random Forest ─────────────────────────────
    # Wrap input in a DataFrame so it has the correct feature names
    input_df = pd.DataFrame(
        [[signal, hour]],
        columns=["signal_strength", "time_hour"]
    )
    
    call_drop = int(rf_model.predict(input_df)[0])
    probs = rf_model.predict_proba(input_df)[0]
    
    if call_drop == 1:
        result = "Call Drop Likely"
        confidence = probs[1] * 100  # confidence in 'drop'
    else:
        result = "No Drop Expected"
        confidence = probs[0] * 100  # confidence in 'complete'

    return jsonify({
        "call_drop":       call_drop,
        "result":          result,
        "confidence":      round(confidence, 1),
        "signal_strength": signal,
        "time_hour":       hour,
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Simple health check."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    print("Starting Live Data Generator Thread...")
    threading.Thread(target=generate_live_data, daemon=True).start()

    print("Starting Telecom Analytics API …")
    print("  GET  /stats   → http://127.0.0.1:5000/stats")
    print("  POST /predict → http://127.0.0.1:5000/predict")
    print("  Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
