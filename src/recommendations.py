
"""
recommendations.py
------------------
Generate explainable household energy-saving recommendations.
"""

from pathlib import Path
import logging

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("Recommendations")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

PEAK_HOURS = range(16, 19)
OFFPEAK_HOURS = range(0, 7)

PEAK_RATE = 0.672
OFFPEAK_RATE = 0.0399
NORMAL_RATE = 0.1176


def tariff(hour):
    if hour in PEAK_HOURS:
        return PEAK_RATE
    if hour in OFFPEAK_HOURS:
        return OFFPEAK_RATE
    return NORMAL_RATE


def estimate_shiftable_load(df):
    temp = df.copy()
    temp["hour"] = temp["tstp"].dt.hour

    peak = (
        temp[temp["hour"].isin(PEAK_HOURS)]
        .groupby("LCLid")["consumption"]
        .mean()
    )

    shift = peak * 0.30 * len(PEAK_HOURS)
    savings = shift * (PEAK_RATE - OFFPEAK_RATE) * 30

    return pd.DataFrame({
        "LCLid": peak.index,
        "avg_peak_kwh": peak.values,
        "shiftable_kwh_day": shift.values,
        "monthly_savings_gbp": savings.round(2).values,
    })


def household_summary(df):
    agg = (
        df.groupby("LCLid")
        .agg(
            avg_consumption=("consumption","mean"),
            weekend_usage=("is_weekend","mean"),
            holiday_usage=("is_holiday","mean"),
        )
    )

    if "Acorn_grouped" in df.columns:
        agg["Acorn_grouped"] = (
            df.groupby("LCLid")["Acorn_grouped"].first()
        )

    if "stdorToU" in df.columns:
        agg["stdorToU"] = (
            df.groupby("LCLid")["stdorToU"].first()
        )

    return agg


def build_message(row):
    rec = []

    if row["monthly_savings_gbp"] > 5:
        rec.append(
            f"Shift approximately {row['shiftable_kwh_day']:.2f} kWh/day from peak to off-peak hours. Estimated monthly saving: £{row['monthly_savings_gbp']:.2f}."
        )

    if row["anomaly_count"] >= 5:
        rec.append(
            f"{int(row['anomaly_count'])} anomalous readings detected. Inspect high-consumption appliances."
        )

    if row["usage_pattern"] == "High Base Load":
        rec.append(
            "High overnight base load detected. Check standby devices and always-on equipment."
        )

    if row["usage_pattern"] == "High Consumption":
        rec.append(
            "Overall electricity usage is higher than similar households. Review HVAC and large appliances."
        )

    if row.get("stdorToU") == "ToU":
        rec.append(
            "Time-of-Use tariff detected. Running flexible appliances during off-peak hours can reduce costs."
        )

    if row.get("Acorn_grouped") == "Affluent":
        rec.append(
            "Compare energy usage with households in the same ACORN segment to identify efficiency opportunities."
        )

    if len(rec) == 0:
        rec.append("Energy usage appears normal. Continue current consumption habits.")

    return " ".join(rec)


def generate_recommendations(
    df,
    anomalies,
    fingerprints,
    cluster_summary,
):
    logger.info("Generating recommendations...")

    shift = estimate_shiftable_load(df)
    summary = household_summary(df)

    anomaly_count = (
        anomalies.groupby("LCLid")
        .size()
        .rename("anomaly_count")
    )

    cluster_labels = (
        fingerprints[["cluster"]]
        .join(cluster_summary["label"], on="cluster")
        .rename(columns={"label":"usage_pattern"})
    )

    rec = (
        shift.set_index("LCLid")
        .join(summary, how="left")
        .join(anomaly_count, how="left")
        .join(cluster_labels[["usage_pattern"]], how="left")
        .fillna({"anomaly_count":0})
        .reset_index()
    )

    rec["recommendation"] = rec.apply(build_message, axis=1)

    rec = rec.sort_values(
        "monthly_savings_gbp",
        ascending=False
    )

    rec.to_csv(
        OUTPUT_DIR/"recommendations.csv",
        index=False
    )

    logger.info(
        "Recommendations generated for %d households",
        len(rec)
    )

    logger.info(
        "Estimated total monthly savings: £%.2f",
        rec["monthly_savings_gbp"].sum()
    )

    return rec


if __name__ == "__main__":
    import clustering
    import anomaly_detection

    df = pd.read_parquet(DATA_DIR/"processed_meter_data.parquet")
    _, anomalies = anomaly_detection.run_anomaly_detection(df)
    fp, summary = clustering.run_clustering(df)
    generate_recommendations(df, anomalies, fp, summary)
