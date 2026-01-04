import sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "data"
OUTPUT_DIR = BASE.parent / "output"

POP_FILE = DATA_DIR / "tamil_nadu_district_demographics.csv"
ACC_FILE = DATA_DIR / "accidents.csv"
OUT_FILE = OUTPUT_DIR / "tn_urban_risk_dataset.csv"

def abort(msg, code=1):
    print("ERROR:", msg)
    sys.exit(code)

for p in (POP_FILE, ACC_FILE):
    if not p.exists():
        abort(f"Required data file not found: {p}\nPlace the file in the project `data/` folder or adjust paths.")

try:
    pop_df = pd.read_csv(POP_FILE)
    acc_df = pd.read_csv(ACC_FILE)
except Exception as e:
    abort(f"Failed to read CSV: {e}")

# required columns
req_pop = {"District", "Population"}
req_acc = {"District", "Total Accidents 2021", "Total Accidents 2022", "Total Accidents 2023"}

if not req_pop.issubset(pop_df.columns):
    abort(f"Missing columns in {POP_FILE}: {req_pop - set(pop_df.columns)}")
if not req_acc.issubset(acc_df.columns):
    abort(f"Missing columns in {ACC_FILE}: {req_acc - set(acc_df.columns)}")

def clean_name(name):
    return str(name).strip().lower()

pop_df["district_clean"] = pop_df["District"].apply(clean_name)
acc_df["district_clean"] = acc_df["District"].apply(clean_name)

district_map = {
    "chennai city": "chennai",
    "chengalpattu": "kancheepuram"
}
acc_df["district_clean"] = acc_df["district_clean"].replace(district_map)

merged = acc_df.merge(
    pop_df[["district_clean", "Population"]],
    on="district_clean",
    how="left"
)

# Ensure numeric population, coerce bad values to NaN
merged["Population"] = pd.to_numeric(merged["Population"], errors="coerce")

missing_pop = merged["Population"].isna().sum()
if missing_pop:
    print(f"Warning: {missing_pop} rows have missing or invalid Population after merge; per-100k will be NaN for those rows.")

for year in ["2021", "2022", "2023"]:
    acc_col = f"Total Accidents {year}"
    out_col = f"accidents_per_100k_{year}"
    merged[out_col] = np.where(
        merged["Population"] > 0,
        (merged[acc_col] / merged["Population"]) * 100_000,
        np.nan
    )

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
merged.to_csv(OUT_FILE, index=False)

print(f"✅ Merged dataset saved in {OUT_FILE}")
