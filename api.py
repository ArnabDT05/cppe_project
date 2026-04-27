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

app = Flask(__name__)
CORS(app)   # allow requests from the React dev server (localhost:5173)

DATA_FILE = "telecom_data.csv"
MODEL_FILE = "rf_model.pkl"

# Load ML model once at startup
if os.path.exists(MODEL_FILE):
    rf_model = joblib.load(MODEL_FILE)
else:
    rf_model = None


def load_stats():
    """Compute all analytics from the CSV and return as a dict."""
    df = pd.read_csv(DATA_FILE)

    total  = len(df)
    drops  = int(df["call_drop"].sum())
    ok     = total - drops

    # ── Hourly distribution ──────────────────────────────────
    hourly = (
        df.groupby("time_hour")["call_drop"]
        .agg(total_calls="count", drops="sum")
        .assign(drop_rate=lambda x: (x["drops"] / x["total_calls"] * 100).round(1))
        .reset_index()
        .rename(columns={"time_hour": "hour"})
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

    return {
        "summary": {
            "total_calls":  total,
            "calls_dropped": drops,
            "calls_completed": ok,
            "drop_pct": round(drops / total * 100, 1),
        },
        "hourly":  hourly.to_dict(orient="records"),
        "towers":  towers.to_dict(orient="records"),
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
    print("Starting Telecom Analytics API …")
    print("  GET  /stats   → http://127.0.0.1:5000/stats")
    print("  POST /predict → http://127.0.0.1:5000/predict")
    print("  Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
