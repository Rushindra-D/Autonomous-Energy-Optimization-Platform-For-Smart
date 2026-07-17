
"""
anomaly_detection.py
--------------------
Hybrid anomaly detection for London Smart Meter data.
"""

from pathlib import Path
import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("AnomalyDetection")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

FEATURES = [
    "consumption",
    "hour",
    "dayofweek",
    "is_weekend",
    "is_holiday",
    "temperature",
    "humidity",
    "windSpeed",
    "pressure",
    "roll_mean_48",
    "roll_std_48",
]


def validate_columns(df):
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def statistical_anomalies(df, threshold=3.0):
    df = df.copy()

    std = df["roll_std_48"].replace(0, np.nan)
    df["zscore"] = (df["consumption"] - df["roll_mean_48"]) / std

    df["zscore_anomaly"] = (
        df["zscore"].abs() >= threshold
    ).astype(int)

    return df


def isolation_forest(df, contamination=0.02):
    df = df.copy()

    model_df = df.dropna(subset=FEATURES)
    MAX_SAMPLES = 500000

    if len(model_df) > MAX_SAMPLES:
        model_df = model_df.sample(
            n=MAX_SAMPLES,
            random_state=42
    )
    logger.info(f"Isolation Forest training rows: {len(model_df):,}")
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )

    pred = model.fit_predict(model_df[FEATURES])
    score = model.decision_function(model_df[FEATURES])

    model_df["iso_anomaly"] = (pred == -1).astype(int)
    model_df["iso_score"] = score

    df = df.merge(
        model_df[
            [
                "LCLid",
                "tstp",
                "iso_anomaly",
                "iso_score",
            ]
        ],
        on=["LCLid", "tstp"],
        how="left",
    )

    return df


def calculate_severity(df):
    df["anomaly_severity"] = (
        df["zscore_anomaly"].fillna(0)
        + df["iso_anomaly"].fillna(0)
    )

    conditions = [
        df["anomaly_severity"] == 2,
        df["anomaly_severity"] == 1,
    ]

    choices = [
        "High",
        "Medium",
    ]

    df["severity_label"] = np.select(
        conditions,
        choices,
        default="Normal",
    )

    return df


def run_anomaly_detection(df):
    validate_columns(df)

    logger.info("Running statistical anomaly detection...")
    df = statistical_anomalies(df)

    logger.info(
        "Z-score anomalies: %d",
        int(df["zscore_anomaly"].sum())
    )

    logger.info("Running Isolation Forest...")
    df = isolation_forest(df)

    logger.info(
        "Isolation Forest anomalies: %d",
        int(df["iso_anomaly"].fillna(0).sum())
    )

    df = calculate_severity(df)

    anomalies = (
        df[df["anomaly_severity"] > 0]
        .sort_values(
            ["anomaly_severity", "iso_score"],
            ascending=[False, True]
        )
    )

    cols = [
        "LCLid",
        "tstp",
        "consumption",
        "roll_mean_48",
        "roll_std_48",
        "zscore",
        "iso_score",
        "anomaly_severity",
        "severity_label",
    ]

    anomalies[cols].to_csv(
        OUTPUT_DIR / "anomalies_detected.csv",
        index=False,
    )

    logger.info(
        "Total anomalies detected: %d",
        len(anomalies),
    )

    return df, anomalies


if __name__ == "__main__":
    df = pd.read_parquet(DATA_DIR / "processed_meter_data.parquet")
    run_anomaly_detection(df)
