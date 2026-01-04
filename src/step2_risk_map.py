import sys
from pathlib import Path
import json
import pandas as pd
import folium

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "data"
OUTPUT_DIR = BASE.parent / "output"

RISK_FILE = OUTPUT_DIR / "tn_urban_risk_dataset.csv"
GEO_FILE = DATA_DIR / "tamil-nadu.geojson"
OUT_HTML = OUTPUT_DIR / "tamil_nadu_accident_risk_map.html"

def abort(msg, code=1):
    print("ERROR:", msg)
    sys.exit(code)

if not RISK_FILE.exists():
    abort(f"Missing input CSV: {RISK_FILE}\nRun the merge step to produce it (step1_merge_and_risk.py).")
if not GEO_FILE.exists():
    abort(f"Missing GeoJSON: {GEO_FILE}")

risk_df = pd.read_csv(RISK_FILE)
with open(GEO_FILE, "r", encoding="utf-8") as f:
    tn_geo = json.load(f)

# Normalize GeoJSON district names
for feature in tn_geo["features"]:
    name = feature["properties"].get("district", "")
    clean = name.lower().replace(" district", "").strip()
    feature["properties"]["district_clean"] = clean

if "district_clean" not in risk_df.columns or "accidents_per_100k_2023" not in risk_df.columns:
    abort("Expected columns 'district_clean' and 'accidents_per_100k_2023' in the risk CSV.")

risk_df["district_clean"] = risk_df["district_clean"].astype(str).str.lower()
risk_lookup = risk_df.set_index("district_clean")["accidents_per_100k_2023"].to_dict()

m = folium.Map(location=[11.1271, 78.6569], zoom_start=7, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=tn_geo,
    data=risk_df,
    columns=["district_clean", "accidents_per_100k_2023"],
    key_on="feature.properties.district_clean",
    fill_color="YlOrRd",
    fill_opacity=0.8,
    line_opacity=0.3,
    legend_name="Accidents per 100k Population (2023)"
).add_to(m)

for feature in tn_geo.get("features", []):
    prop = feature.get("properties", {})
    disp_name = prop.get("district", prop.get("DISTRICT", "Unknown"))
    d_name = str(disp_name).lower().replace(" district", "").strip()
    risk = risk_lookup.get(d_name, "No data")
    folium.GeoJson(
        feature,
        tooltip=folium.Tooltip(f"District: {disp_name}<br>Accidents per 100k (2023): {risk}")
    ).add_to(m)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
m.save(OUT_HTML)
print(f"✅ Map saved: {OUT_HTML}")

