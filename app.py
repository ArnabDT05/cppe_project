"""
app.py
------
Streamlit dashboard for Telecom Call Drop Analytics.

Sections
--------
1. KPI cards  — overall call drop stats
2. Line chart — call drops vs Hour of Day
3. Table      — Top 5 towers with highest drops
4. Predictor  — live call-drop prediction using trained RandomForest
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.ensemble      import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Telecom Call Drop Analytics",
    page_icon="📡",
    layout="wide",
)

# ── Custom CSS — dark premium theme ───────────────────────────────
st.markdown("""
<style>
/* ---- Global ---- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d1a;
    color: #e0e0f0;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] { background-color: #12122a; }

/* ---- Header ---- */
.dash-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.dash-sub {
    color: #8888aa;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* ---- KPI cards ---- */
.kpi-card {
    background: linear-gradient(135deg, #1a1a3e 0%, #12122a 100%);
    border: 1px solid #2a2a5a;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.kpi-label { font-size: 0.8rem; color: #8888aa; text-transform: uppercase; letter-spacing: 1px; }
.kpi-value { font-size: 2rem;   font-weight: 800; color: #00d4ff; margin: 0.3rem 0; }
.kpi-value.red   { color: #ff6b6b; }
.kpi-value.green { color: #00e676; }

/* ---- Section headers ---- */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #c0c0e0;
    border-left: 4px solid #00d4ff;
    padding-left: 0.6rem;
    margin: 1.5rem 0 0.8rem;
}

/* ---- Prediction result ---- */
.pred-drop {
    background: linear-gradient(135deg, #3a0000, #200000);
    border: 2px solid #ff6b6b;
    border-radius: 14px;
    padding: 1.4rem 2rem;
    font-size: 1.4rem;
    font-weight: 800;
    color: #ff6b6b;
    text-align: center;
}
.pred-ok {
    background: linear-gradient(135deg, #003a00, #002000);
    border: 2px solid #00e676;
    border-radius: 14px;
    padding: 1.4rem 2rem;
    font-size: 1.4rem;
    font-weight: 800;
    color: #00e676;
    text-align: center;
}
.pred-conf { font-size: 0.95rem; font-weight: 400; margin-top: 0.4rem; color: #aaaacc; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 0. Load data & train model (cached so it runs only once)
# ══════════════════════════════════════════════════════════════════
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and return the telecom CSV dataset."""
    return pd.read_csv("telecom_data.csv")


@st.cache_resource
def train_model(df: pd.DataFrame) -> RandomForestClassifier:
    """Train a RandomForest on signal_strength + time_hour and return it."""
    X = df[["signal_strength", "time_hour"]]
    y = df["call_drop"]
    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)
    return clf


df    = load_data()
model = train_model(df)

# ── Pre-compute aggregates ─────────────────────────────────────────
total        = len(df)
total_drops  = int(df["call_drop"].sum())
total_ok     = total - total_drops
drop_pct     = round(total_drops / total * 100, 1)

hourly = (
    df.groupby("time_hour")["call_drop"]
    .agg(total_calls="count", drops="sum")
    .assign(drop_rate=lambda x: (x["drops"] / x["total_calls"] * 100).round(1))
    .reset_index()
)

top5_towers = (
    df.groupby("tower_id")["call_drop"]
    .agg(total_calls="count", drops="sum")
    .assign(drop_rate_pct=lambda x: (x["drops"] / x["total_calls"] * 100).round(1))
    .sort_values("drops", ascending=False)
    .head(5)
    .reset_index()
    .rename(columns={
        "tower_id":      "Tower ID",
        "total_calls":   "Total Calls",
        "drops":         "Call Drops",
        "drop_rate_pct": "Drop Rate (%)",
    })
)


# ══════════════════════════════════════════════════════════════════
# 1. Header
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="dash-title">📡 Telecom Call Drop Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="dash-sub">Chennai Region · Synthetic Dataset · RandomForest Predictor</p>', unsafe_allow_html=True)
st.divider()


# ══════════════════════════════════════════════════════════════════
# 2. KPI Cards
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">📊 Key Metrics</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Calls</div>
        <div class="kpi-value">{total:,}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Calls Dropped</div>
        <div class="kpi-value red">{total_drops:,}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Calls Completed</div>
        <div class="kpi-value green">{total_ok:,}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Call Drop %</div>
        <div class="kpi-value red">{drop_pct}%</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 3. Line Chart — Call Drops vs Hour of Day
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🕐 Call Drops vs Hour of Day</p>', unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(12, 4))
fig.patch.set_facecolor("#0d0d1a")
ax.set_facecolor("#1a1a2e")

# Filled area + line for drop count
ax.fill_between(hourly["time_hour"], hourly["drops"], alpha=0.2, color="#00d4ff")
ax.plot(
    hourly["time_hour"], hourly["drops"],
    color="#00d4ff", linewidth=2.5,
    marker="o", markersize=6,
    markerfacecolor="#0d0d1a", markeredgewidth=2, markeredgecolor="#00d4ff",
    label="Drop Count",
)

# Secondary axis — drop rate %
ax2 = ax.twinx()
ax2.plot(
    hourly["time_hour"], hourly["drop_rate"],
    color="#ff9f43", linewidth=1.8, linestyle="--",
    marker="s", markersize=4,
    markerfacecolor="#0d0d1a", markeredgewidth=1.5, markeredgecolor="#ff9f43",
    label="Drop Rate %",
)
ax2.set_ylabel("Drop Rate (%)", color="#ff9f43", fontsize=10)
ax2.tick_params(axis="y", labelcolor="#ff9f43")
ax2.set_facecolor("#1a1a2e")

# Peak annotation
peak = hourly.loc[hourly["drops"].idxmax()]
ax.annotate(
    f"Peak\n{int(peak['time_hour']):02d}:00\n{int(peak['drops'])} drops",
    xy=(peak["time_hour"], peak["drops"]),
    xytext=(peak["time_hour"] + 1, peak["drops"] + 1.2),
    arrowprops=dict(arrowstyle="->", color="#ff6b6b", lw=1.4),
    fontsize=8, color="#ff6b6b",
)

for spine in ax.spines.values():
    spine.set_edgecolor("#2a2a5a")
ax.set_xlabel("Hour of Day", color="#c0c0e0")
ax.set_ylabel("Number of Call Drops", color="#00d4ff")
ax.tick_params(colors="#c0c0e0")
ax.set_xticks(range(0, 24))
ax.set_xticklabels([f"{h:02d}" for h in range(24)])
ax.grid(color="#2a2a5a", linestyle="--", alpha=0.5)
ax.set_title("Hourly Call Drop Distribution", color="#e0e0f0", fontweight="bold", pad=10)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, facecolor="#1a1a2e",
          edgecolor="#2a2a5a", labelcolor="#c0c0e0", fontsize=9)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)


# ══════════════════════════════════════════════════════════════════
# 4. Top 5 Towers Table
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🗼 Top 5 Towers — Highest Call Drops</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.4, 1])

with col_left:
    st.dataframe(
        top5_towers,
        use_container_width=True,
        hide_index=True,
    )

with col_right:
    # Mini bar chart for the top-5 towers
    fig2, ax3 = plt.subplots(figsize=(5, 3.2))
    fig2.patch.set_facecolor("#0d0d1a")
    ax3.set_facecolor("#1a1a2e")

    colors = ["#ff6b6b", "#ff9f43", "#ffcc00", "#00d4ff", "#00e676"]
    ax3.barh(
        top5_towers["Tower ID"],
        top5_towers["Call Drops"],
        color=colors, edgecolor="#0d0d1a",
    )
    ax3.set_xlabel("Call Drops", color="#c0c0e0")
    ax3.tick_params(colors="#c0c0e0")
    for spine in ax3.spines.values():
        spine.set_edgecolor("#2a2a5a")
    ax3.grid(axis="x", color="#2a2a5a", linestyle="--", alpha=0.5)
    ax3.set_title("Drop Count", color="#e0e0f0", fontsize=10, fontweight="bold")
    ax3.invert_yaxis()
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)


# ══════════════════════════════════════════════════════════════════
# 5. Live Call Drop Predictor
# ══════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<p class="section-title">🔮 Live Call Drop Predictor</p>', unsafe_allow_html=True)

with st.container():
    p1, p2, p3 = st.columns([1, 1, 1])

    with p1:
        signal = st.slider(
            "Signal Strength (dBm)",
            min_value=-110, max_value=-70, value=-100, step=1,
            help="Values below −95 dBm are considered weak and likely to cause drops.",
        )
    with p2:
        hour = st.slider(
            "Hour of Day",
            min_value=0, max_value=23, value=18, step=1,
            format="%02d:00",
            help="Peak hours are 08:00, 16:00–21:00.",
        )
    with p3:
        st.markdown("<br>", unsafe_allow_html=True)   # vertical align
        predict_btn = st.button("⚡ Predict Call Drop", use_container_width=True)

    # ── Prediction result ─────────────────────────────────────────
    if predict_btn:
        sample = pd.DataFrame(
            [[signal, hour]],
            columns=["signal_strength", "time_hour"],
        )
        pred      = model.predict(sample)[0]
        proba     = model.predict_proba(sample)[0]   # [P(complete), P(drop)]
        drop_prob = proba[1] * 100

        if pred == 1:
            st.markdown(f"""
            <div class="pred-drop">
                ⚠️ &nbsp; CALL DROP LIKELY
                <div class="pred-conf">
                    Signal: {signal} dBm &nbsp;|&nbsp; Hour: {hour:02d}:00
                    &nbsp;|&nbsp; Drop probability: <b>{drop_prob:.1f}%</b>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="pred-ok">
                ✅ &nbsp; CALL WILL COMPLETE — NO DROP
                <div class="pred-conf">
                    Signal: {signal} dBm &nbsp;|&nbsp; Hour: {hour:02d}:00
                    &nbsp;|&nbsp; Drop probability: <b>{drop_prob:.1f}%</b>
                </div>
            </div>""", unsafe_allow_html=True)

        # Confidence gauge bar
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(int(drop_prob), text=f"Drop confidence: {drop_prob:.1f}%")

# ── Footer ────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center style='color:#444466;font-size:0.8rem;'>"
    "Telecom Call Drop Analytics · Chennai Dataset · RandomForest v1.0"
    "</center>",
    unsafe_allow_html=True,
)
