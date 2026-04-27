"""
analysis.py
-----------
Analyses the synthetic Chennai telecom dataset (telecom_data.csv).

Steps
-----
1. Load telecom_data.csv
2. Calculate overall call drop percentage
3. Group by tower_id  → count drops per tower, show top 5
4. Group by time_hour → hourly drop distribution
5. Print all results to console
"""

import pandas as pd

# ------------------------------------------------------------------
# 1. Load Data
# ------------------------------------------------------------------
DATA_FILE = "telecom_data.csv"

print("=" * 58)
print("   TELECOM CALL DROP ANALYSIS — Chennai Dataset")
print("=" * 58)

df = pd.read_csv(DATA_FILE)

print(f"\n✔ Loaded '{DATA_FILE}'")
print(f"  Rows    : {len(df)}")
print(f"  Columns : {list(df.columns)}")


# ------------------------------------------------------------------
# 2. Overall Call Drop Percentage
# ------------------------------------------------------------------
print("\n" + "─" * 58)
print("SECTION 1 — OVERALL CALL DROP STATISTICS")
print("─" * 58)

total_calls    = len(df)
total_drops    = df["call_drop"].sum()           # sum of 1s = number of drops
total_complete = total_calls - total_drops
drop_pct       = (total_drops / total_calls) * 100

print(f"\n  Total calls          : {total_calls}")
print(f"  Calls completed      : {total_complete}  ({100 - drop_pct:.1f}%)")
print(f"  Calls dropped        : {total_drops}   ({drop_pct:.1f}%)")
print(f"\n  ➜ Call Drop Percentage : {drop_pct:.2f}%")


# ------------------------------------------------------------------
# 3. Group by tower_id — drop count per tower
# ------------------------------------------------------------------
print("\n" + "─" * 58)
print("SECTION 2 — CALL DROPS BY TOWER (Top 5)")
print("─" * 58)

# For every tower: count total calls, sum drops, compute drop rate
tower_stats = (
    df.groupby("tower_id")
    .agg(
        total_calls=("call_drop", "count"),
        total_drops=("call_drop", "sum"),
    )
    .assign(drop_rate_pct=lambda x: (x["total_drops"] / x["total_calls"] * 100).round(2))
    .sort_values("total_drops", ascending=False)   # rank by raw drop count
    .reset_index()
)

# Top 5 towers with the highest number of drops
top5_towers = tower_stats.head(5)

print(f"\n{'Rank':<6}{'Tower ID':<14}{'Total Calls':>12}{'Drops':>8}{'Drop Rate':>12}")
print("-" * 52)
for rank, row in enumerate(top5_towers.itertuples(), start=1):
    bar = "█" * int(row.drop_rate_pct / 5)       # ASCII progress bar
    print(
        f"  {rank:<4}{row.tower_id:<14}"
        f"{row.total_calls:>12}{row.total_drops:>8}"
        f"{row.drop_rate_pct:>10.1f}%  {bar}"
    )

# Signal strength stats for these top-5 towers (diagnostic context)
print("\n  Average signal strength for top-5 drop towers:")
top5_ids     = top5_towers["tower_id"].tolist()
sig_for_top5 = (
    df[df["tower_id"].isin(top5_ids)]
    .groupby("tower_id")["signal_strength"]
    .mean()
    .round(2)
)
for tower, avg_sig in sig_for_top5.items():
    print(f"    {tower} → avg signal = {avg_sig} dBm")


# ------------------------------------------------------------------
# 4. Group by time_hour — hourly drop distribution
# ------------------------------------------------------------------
print("\n" + "─" * 58)
print("SECTION 3 — HOURLY CALL DROP DISTRIBUTION")
print("─" * 58)

hourly_stats = (
    df.groupby("time_hour")
    .agg(
        total_calls=("call_drop", "count"),
        total_drops=("call_drop", "sum"),
    )
    .assign(drop_rate_pct=lambda x: (x["total_drops"] / x["total_calls"] * 100).round(2))
    .reset_index()
)

print(f"\n{'Hour':<8}{'Total Calls':>12}{'Drops':>8}{'Drop Rate':>12}  {'Chart'}")
print("-" * 70)

for row in hourly_stats.itertuples():
    bar   = "▓" * int(row.drop_rate_pct / 3)     # scale bar to fit console
    label = f"{row.time_hour:02d}:00"
    print(
        f"  {label:<8}"
        f"{row.total_calls:>12}"
        f"{row.total_drops:>8}"
        f"{row.drop_rate_pct:>10.1f}%  {bar}"
    )

# Peak & off-peak hours
peak_hour    = hourly_stats.loc[hourly_stats["total_drops"].idxmax()]
offpeak_hour = hourly_stats.loc[hourly_stats["total_drops"].idxmin()]

print(f"\n  ➜ Highest drop hour : {int(peak_hour['time_hour']):02d}:00  "
      f"({int(peak_hour['total_drops'])} drops, {peak_hour['drop_rate_pct']:.1f}%)")
print(f"  ➜ Lowest  drop hour : {int(offpeak_hour['time_hour']):02d}:00  "
      f"({int(offpeak_hour['total_drops'])} drops, {offpeak_hour['drop_rate_pct']:.1f}%)")


# ------------------------------------------------------------------
# 5. Quick Signal Strength Summary
# ------------------------------------------------------------------
print("\n" + "─" * 58)
print("SECTION 4 — SIGNAL STRENGTH SUMMARY")
print("─" * 58)

# Compare average signal for dropped vs completed calls
sig_by_status = df.groupby("call_drop")["signal_strength"].agg(["mean", "min", "max"]).round(2)
sig_by_status.index = ["Completed (0)", "Dropped (1)"]

print(f"\n{'Status':<18}{'Mean (dBm)':>12}{'Min (dBm)':>12}{'Max (dBm)':>12}")
print("-" * 54)
for status, row in sig_by_status.iterrows():
    print(f"  {status:<18}{row['mean']:>12}{row['min']:>12}{row['max']:>12}")

print("\n✔ Analysis complete. Run visualization.py to see charts.\n")
