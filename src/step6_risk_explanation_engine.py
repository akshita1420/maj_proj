from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE.parent / "output"

INPUT_FILE = OUTPUT_DIR / "tn_urban_risk_dataset.csv"
OUT_FILE = OUTPUT_DIR / "tn_risk_explanation.csv"

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(INPUT_FILE)

# Select relevant columns
cols = [
    "District",
    "Population",
    "Total Accidents 2023",
    "accidents_per_100k_2023"
]

df = df[cols].dropna()

# -----------------------------
# Standardize factors (Z-score)
# -----------------------------
def zscore(series):
    return (series - series.mean()) / series.std()

df["z_population"] = zscore(df["Population"])
df["z_total_accidents"] = zscore(df["Total Accidents 2023"])
df["z_risk"] = zscore(df["accidents_per_100k_2023"])

# -----------------------------
# Contribution analysis
# -----------------------------
df["population_contribution"] = abs(df["z_population"] * df["z_risk"])
df["accident_volume_contribution"] = abs(df["z_total_accidents"] * df["z_risk"])

# Normalize contributions
total = df["population_contribution"] + df["accident_volume_contribution"]
df["population_weight"] = df["population_contribution"] / total
df["accident_volume_weight"] = df["accident_volume_contribution"] / total

# -----------------------------
# Dominant factor (DATA-DRIVEN)
# -----------------------------
df["dominant_risk_driver"] = np.where(
    df["population_weight"] > df["accident_volume_weight"],
    "Population Exposure",
    "Accident Intensity"
)

# -----------------------------
# Save result
# -----------------------------
df.to_csv(OUT_FILE, index=False)

print("✅ Risk explanation engine completed")
print("📁 Output saved:", OUT_FILE)
