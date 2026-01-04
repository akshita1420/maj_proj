from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE.parent / "output"

RISK_FILE = OUTPUT_DIR / "tn_urban_risk_dataset.csv"
EXPL_FILE = OUTPUT_DIR / "tn_risk_explanation.csv"
OUT_FILE = OUTPUT_DIR / "tn_decision_support_priorities.csv"

# -----------------------------
# Load data
# -----------------------------
risk_df = pd.read_csv(RISK_FILE)
expl_df = pd.read_csv(EXPL_FILE)

# -----------------------------
# Merge explanation with risk
# -----------------------------
df = risk_df.merge(
    expl_df[[
        "District",
        "population_weight",
        "accident_volume_weight",
        "dominant_risk_driver"
    ]],
    on="District",
    how="inner"
)

# -----------------------------
# Define impact score (data-driven)
# -----------------------------
df["impact_score"] = (
    df["accidents_per_100k_2023"] *
    np.maximum(df["population_weight"], df["accident_volume_weight"])
)

# -----------------------------
# Rank districts by impact
# -----------------------------
df = df.sort_values("impact_score", ascending=False).reset_index(drop=True)

# -----------------------------
# Cumulative impact coverage
# -----------------------------
df["cumulative_impact"] = df["impact_score"].cumsum()
total_impact = df["impact_score"].sum()
df["cumulative_impact_pct"] = df["cumulative_impact"] / total_impact

# -----------------------------
# Policy priority (NO FIXED CUT-OFF)
# -----------------------------
df["policy_priority"] = np.where(
    df["cumulative_impact_pct"] <= 0.6,
    "High Priority Intervention Zone",
    "Secondary Monitoring Zone"
)

# -----------------------------
# Save output
# -----------------------------
df.to_csv(OUT_FILE, index=False)

print("✅ Decision support simulation completed")
print("📁 Output saved:", OUT_FILE)
