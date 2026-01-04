from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans

BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE.parent / "output"

RISK_FILE = OUTPUT_DIR / "tn_urban_risk_dataset.csv"
OUT_FILE = OUTPUT_DIR / "tn_urban_risk_with_clusters.csv"

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv(RISK_FILE)

# Use latest year for clustering
feature_col = "accidents_per_100k_2023"

# Drop rows with missing values
cluster_df = df[["District", feature_col]].dropna()

# -----------------------------
# Apply K-Means clustering
# -----------------------------
kmeans = KMeans(n_clusters=3, random_state=42)
cluster_df["risk_cluster"] = kmeans.fit_predict(cluster_df[[feature_col]])

# -----------------------------
# Map cluster labels to meaning
# -----------------------------
cluster_means = cluster_df.groupby("risk_cluster")[feature_col].mean().sort_values()

cluster_map = {
    cluster_means.index[0]: "Low Risk",
    cluster_means.index[1]: "Medium Risk",
    cluster_means.index[2]: "High Risk"
}

cluster_df["risk_level"] = cluster_df["risk_cluster"].map(cluster_map)

# -----------------------------
# Merge back to main dataset
# -----------------------------
final_df = df.merge(
    cluster_df[["District", "risk_level"]],
    on="District",
    how="left"
)

final_df.to_csv(OUT_FILE, index=False)

print("✅ AI clustering completed")
print("📁 Output saved:", OUT_FILE)
