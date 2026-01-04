from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE.parent / "output"

INPUT_FILE = OUTPUT_DIR / "tn_urban_risk_dataset.csv"
OUT_FILE = OUTPUT_DIR / "tn_temporal_risk_intelligence.csv"

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(INPUT_FILE)

# -----------------------------
# Calculate temporal change
# -----------------------------
df["risk_change_21_23"] = (
    df["accidents_per_100k_2023"] - df["accidents_per_100k_2021"]
)

# -----------------------------
# Classify temporal patterns
# -----------------------------
def classify_trend(val):
    if pd.isna(val):
        return "Insufficient Data"
    elif val > 20:
        return "Emerging High Risk"
    elif val > 0:
        return "Gradually Increasing Risk"
    elif val < -20:
        return "Significantly Improving"
    else:
        return "Stable / Minor Change"

df["risk_trend_category"] = df["risk_change_21_23"].apply(classify_trend)

# -----------------------------
# Save output
# -----------------------------
df.to_csv(OUT_FILE, index=False)

print("✅ Temporal risk intelligence generated")
print("📁 Output saved:", OUT_FILE)
