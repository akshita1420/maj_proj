from pathlib import Path
import json
import pandas as pd
import folium

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "data"
OUTPUT_DIR = BASE.parent / "output"

CLUSTER_FILE = OUTPUT_DIR / "tn_urban_risk_with_clusters.csv"
GEO_FILE = DATA_DIR / "tamil-nadu.geojson"
OUT_HTML = OUTPUT_DIR / "tamil_nadu_ai_risk_clusters.html"

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(CLUSTER_FILE)

with open(GEO_FILE, "r", encoding="utf-8") as f:
    tn_geo = json.load(f)

# Normalize names
df["district_clean"] = df["District"].astype(str).str.lower()

for feature in tn_geo["features"]:
    name = feature["properties"].get("district", "")
    feature["properties"]["district_clean"] = name.lower().replace(" district", "").strip()

# Risk color mapping
risk_colors = {
    "High Risk": "#d73027",
    "Medium Risk": "#fc8d59",
    "Low Risk": "#1a9850"
}

# -----------------------------
# Create map
# -----------------------------
m = folium.Map(location=[11.1271, 78.6569], zoom_start=7, tiles="cartodbpositron")

for feature in tn_geo["features"]:
    d_clean = feature["properties"]["district_clean"]
    row = df[df["district_clean"] == d_clean]

    if not row.empty:
        risk = row.iloc[0]["risk_level"]
        color = risk_colors.get(risk, "#cccccc")
    else:
        risk = "No Data"
        color = "#cccccc"

    folium.GeoJson(
        feature,
        style_function=lambda x, c=color: {
            "fillColor": c,
            "color": "blue",
            "weight": 1,
            "fillOpacity": 0.8
        },
        tooltip=folium.Tooltip(
            f"District: {feature['properties'].get('district')}<br>AI Risk Level: {risk}"
        )
    ).add_to(m)

# -----------------------------
# Save map
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
m.save(OUT_HTML)

print("✅ AI Cluster Map saved:", OUT_HTML)
