from pathlib import Path
import pandas as pd

# ----------------------------------------------------
# Paths
# ----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

FULL_DATA = DATA_DIR / "processed_meter_data.parquet"

DASHBOARD_DATA = DATA_DIR / "dashboard_data.parquet"

# ----------------------------------------------------
# Load Full Dataset
# ----------------------------------------------------

print("Loading full dataset...")

df = pd.read_parquet(FULL_DATA)

print(f"Original Shape : {df.shape}")

# ----------------------------------------------------
# Random Sample
# ----------------------------------------------------

SAMPLE_SIZE = 50000

if len(df) > SAMPLE_SIZE:
    dashboard_df = df.sample(
        n=SAMPLE_SIZE,
        random_state=42
    )
else:
    dashboard_df = df.copy()

# ----------------------------------------------------
# Sort by timestamp (optional)
# ----------------------------------------------------

if "tstp" in dashboard_df.columns:
    dashboard_df = dashboard_df.sort_values("tstp")

# ----------------------------------------------------
# Save
# ----------------------------------------------------

dashboard_df.to_parquet(
    DASHBOARD_DATA,
    index=False
)

print("Dashboard dataset created successfully!")

print(f"Dashboard Shape : {dashboard_df.shape}")

print(f"Saved to : {DASHBOARD_DATA}")