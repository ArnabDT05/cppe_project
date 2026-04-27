"""
visualization.py
----------------
Visualises call-drop patterns from the Chennai telecom dataset.

Charts produced
---------------
1. Line plot  — Call drops vs Hour of Day
2. Bar chart  — Top 10 towers with highest call drops

Charts are both displayed (plt.show) and saved as PNG files
in the 'charts/' directory for later reference.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # non-interactive backend — safe for terminal/scripts
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ------------------------------------------------------------------
# Global Style — clean dark theme
# ------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor":  "#0f0f1a",
    "axes.facecolor":    "#1a1a2e",
    "axes.edgecolor":    "#44475a",
    "axes.labelcolor":   "#f8f8f2",
    "axes.titlecolor":   "#f8f8f2",
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "axes.labelsize":    12,
    "xtick.color":       "#f8f8f2",
    "ytick.color":       "#f8f8f2",
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "grid.color":        "#2e2e4e",
    "grid.linestyle":    "--",
    "grid.alpha":        0.6,
    "legend.facecolor":  "#1a1a2e",
    "legend.edgecolor":  "#44475a",
    "legend.fontsize":   10,
    "font.family":       "DejaVu Sans",
})

# Colour accents
CYAN   = "#00d4ff"
ORANGE = "#ff9f43"
RED    = "#ff6b6b"

# ------------------------------------------------------------------
# 0. Setup
# ------------------------------------------------------------------
DATA_FILE  = "telecom_data.csv"
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

print("Loading data …")
df = pd.read_csv(DATA_FILE)
print(f"  ✔ {len(df)} rows loaded from '{DATA_FILE}'\n")


# ------------------------------------------------------------------
# CHART 1 — Line plot: Call drops vs Hour of Day
# ------------------------------------------------------------------
print("[1/2] Generating Line Plot — Call Drops vs Hour of Day …")

# Aggregate: count drops and total calls per hour
hourly = (
    df.groupby("time_hour")
    .agg(
        total_calls=("call_drop", "count"),
        drops=("call_drop", "sum"),
    )
    .assign(drop_rate_pct=lambda x: (x["drops"] / x["total_calls"] * 100).round(2))
    .reset_index()
)

fig1, ax1 = plt.subplots(figsize=(13, 5))
fig1.suptitle("", fontsize=1)   # spacer

# Filled area under the drop count line
ax1.fill_between(
    hourly["time_hour"],
    hourly["drops"],
    alpha=0.18,
    color=CYAN,
    label="_nolegend_",
)

# Main line — drop count
ax1.plot(
    hourly["time_hour"],
    hourly["drops"],
    color=CYAN,
    linewidth=2.5,
    marker="o",
    markersize=7,
    markerfacecolor="#0f0f1a",
    markeredgewidth=2,
    markeredgecolor=CYAN,
    label="Drop Count",
    zorder=3,
)

# Secondary line — drop rate %
ax2 = ax1.twinx()
ax2.plot(
    hourly["time_hour"],
    hourly["drop_rate_pct"],
    color=ORANGE,
    linewidth=1.8,
    linestyle="--",
    marker="s",
    markersize=5,
    markerfacecolor="#0f0f1a",
    markeredgewidth=1.5,
    markeredgecolor=ORANGE,
    label="Drop Rate %",
    zorder=2,
)
ax2.set_ylabel("Drop Rate (%)", color=ORANGE, fontsize=12)
ax2.tick_params(axis="y", labelcolor=ORANGE)
ax2.set_facecolor("#1a1a2e")

# Annotate the peak hour
peak_row = hourly.loc[hourly["drops"].idxmax()]
ax1.annotate(
    f"Peak: {int(peak_row['time_hour']):02d}:00\n{int(peak_row['drops'])} drops",
    xy=(peak_row["time_hour"], peak_row["drops"]),
    xytext=(peak_row["time_hour"] + 1.2, peak_row["drops"] + 1.5),
    arrowprops=dict(arrowstyle="->", color=RED, lw=1.5),
    fontsize=9,
    color=RED,
)

# Formatting
ax1.set_title("Call Drops vs Hour of Day (Chennai Telecom Dataset)", pad=12)
ax1.set_xlabel("Hour of Day")
ax1.set_ylabel("Number of Call Drops", color=CYAN, fontsize=12)
ax1.tick_params(axis="y", labelcolor=CYAN)
ax1.set_xticks(range(0, 24))
ax1.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, ha="right")
ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax1.grid(True, axis="both")
ax1.set_xlim(-0.5, 23.5)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()

# Save
path1 = os.path.join(CHARTS_DIR, "01_drops_vs_hour.png")
fig1.savefig(path1, dpi=150, bbox_inches="tight")
print(f"  ✔ Saved → {path1}")
plt.show()


# ------------------------------------------------------------------
# CHART 2 — Bar chart: Top 10 towers with highest call drops
# ------------------------------------------------------------------
print("\n[2/2] Generating Bar Chart — Top 10 Towers by Call Drops …")

# Aggregate per tower
tower_stats = (
    df.groupby("tower_id")
    .agg(
        total_calls=("call_drop", "count"),
        drops=("call_drop", "sum"),
    )
    .assign(drop_rate_pct=lambda x: (x["drops"] / x["total_calls"] * 100).round(1))
    .sort_values("drops", ascending=False)
    .head(10)
    .reset_index()
)

fig2, ax3 = plt.subplots(figsize=(12, 6))

# Colour bars by drop rate: higher rate → more red
colours = [
    f"#{int(255 * (r / 100)):02x}{int(255 * (1 - r / 100)):02x}88"
    for r in tower_stats["drop_rate_pct"]
]

bars = ax3.bar(
    tower_stats["tower_id"],
    tower_stats["drops"],
    color=colours,
    edgecolor="#0f0f1a",
    linewidth=0.8,
    width=0.6,
    zorder=3,
)

# Value labels on top of each bar
for bar, drops, rate in zip(bars, tower_stats["drops"], tower_stats["drop_rate_pct"]):
    ax3.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{drops}\n({rate}%)",
        ha="center", va="bottom",
        fontsize=9, color="#f8f8f2",
    )

# Formatting
ax3.set_title("Top 10 Cell Towers — Highest Call Drops (Chennai Dataset)", pad=12)
ax3.set_xlabel("Tower ID")
ax3.set_ylabel("Number of Call Drops")
ax3.set_xticks(range(len(tower_stats)))
ax3.set_xticklabels(tower_stats["tower_id"], rotation=30, ha="right")
ax3.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax3.grid(True, axis="y")
ax3.set_ylim(0, tower_stats["drops"].max() + 3)

# Colour legend (low → high)
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#ff008888", label="High drop rate (≈100%)"),
    Patch(facecolor="#ffaa0088", label="Medium drop rate"),
    Patch(facecolor="#00ff0088", label="Lower drop rate"),
]
ax3.legend(handles=legend_elements, loc="upper right")

plt.tight_layout()

# Save
path2 = os.path.join(CHARTS_DIR, "02_top10_towers_drops.png")
fig2.savefig(path2, dpi=150, bbox_inches="tight")
print(f"  ✔ Saved → {path2}")
plt.show()

print(f"\n✔ Both charts displayed and saved to '{CHARTS_DIR}/' directory.\n")
