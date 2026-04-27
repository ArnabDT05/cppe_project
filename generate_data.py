"""
generate_data.py
----------------
Generates a synthetic telecom dataset centred around Chennai, India.

Columns
-------
tower_id        : Unique cell-tower identifier  (e.g. TOWER_0001)
latitude        : Tower latitude  — Chennai range [12.8, 13.2]
longitude       : Tower longitude — Chennai range [80.1, 80.3]
signal_strength : Received signal level in dBm  [-110, -70]
time_hour       : Hour of the day the reading was captured  [0, 23]
call_drop       : 1 if signal_strength < -95 dBm (weak signal), else 0

Output
------
telecom_data.csv  (saved in the current working directory)
"""

import pandas as pd
import numpy as np
import os

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
NUM_ROWS    = 1000                      # Total records to generate
OUTPUT_FILE = "telecom_data.csv"        # Output CSV filename
SEED        = 42                        # Random seed for reproducibility

# Chennai geographic bounding box
LAT_MIN,  LAT_MAX  = 12.8, 13.2        # Latitude  range
LON_MIN,  LON_MAX  = 80.1, 80.3        # Longitude range

# Signal strength range (dBm)
SIG_MIN,  SIG_MAX  = -110, -70

# Call-drop threshold: signal below this → call_drop = 1
DROP_THRESHOLD = -95                    # dBm


def generate_telecom_data(n: int = NUM_ROWS) -> pd.DataFrame:
    """
    Build the synthetic telecom DataFrame.

    Parameters
    ----------
    n : int
        Number of rows to generate.

    Returns
    -------
    pd.DataFrame
    """
    np.random.seed(SEED)

    # --- Tower IDs ---
    # Zero-padded numeric IDs: TOWER_0001 … TOWER_1000
    tower_ids = [f"TOWER_{i:04d}" for i in range(1, n + 1)]

    # --- Geographic coordinates (uniform random within Chennai bbox) ---
    latitudes  = np.random.uniform(LAT_MIN,  LAT_MAX,  n).round(6)
    longitudes = np.random.uniform(LON_MIN,  LON_MAX,  n).round(6)

    # --- Signal strength (uniform random between -110 and -70 dBm) ---
    signal_strength = np.random.uniform(SIG_MIN, SIG_MAX, n).round(2)

    # --- Time of day (integer hour 0–23) ---
    time_hour = np.random.randint(0, 24, n)

    # --- Call drop label (deterministic rule based on signal strength) ---
    # 1 = dropped (weak signal), 0 = completed (adequate signal)
    call_drop = (signal_strength < DROP_THRESHOLD).astype(int)

    # --- Assemble DataFrame ---
    df = pd.DataFrame({
        "tower_id":        tower_ids,
        "latitude":        latitudes,
        "longitude":       longitudes,
        "signal_strength": signal_strength,
        "time_hour":       time_hour,
        "call_drop":       call_drop,
    })

    return df


if __name__ == "__main__":
    print("Generating synthetic Chennai telecom dataset …")

    df = generate_telecom_data(NUM_ROWS)

    # Save to CSV (no index column)
    df.to_csv(OUTPUT_FILE, index=False)

    # ── Summary ────────────────────────────────────────────────────
    total_drops = df["call_drop"].sum()
    drop_pct    = total_drops / NUM_ROWS * 100

    print(f"\n  Rows generated        : {NUM_ROWS}")
    print(f"  Columns               : {list(df.columns)}")
    print(f"  Latitude  range       : [{df['latitude'].min():.4f}, {df['latitude'].max():.4f}]")
    print(f"  Longitude range       : [{df['longitude'].min():.4f}, {df['longitude'].max():.4f}]")
    print(f"  Signal range (dBm)    : [{df['signal_strength'].min()}, {df['signal_strength'].max()}]")
    print(f"  Drop threshold        : signal_strength < {DROP_THRESHOLD} dBm")
    print(f"  Call drops (label=1)  : {total_drops} ({drop_pct:.1f}%)")
    print(f"  Calls completed (0)   : {NUM_ROWS - total_drops} ({100 - drop_pct:.1f}%)")
    print(f"\n  Saved → {os.path.abspath(OUTPUT_FILE)}")

    print("\nFirst 10 rows:")
    print(df.head(10).to_string(index=False))
