"""
data_loader.py
--------------
Loads processed dataset and all pipeline outputs.

Author: Rushindra Dobila
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

OUTPUT_DIR = BASE_DIR / "outputs"

PROCESSED_DATA = DATA_DIR / "dashboard_data.parquet"


# -------------------------------------------------------------------
# Generic CSV Loader
# -------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_csv(filename):

    file = OUTPUT_DIR / filename

    if file.exists():
        return pd.read_csv(file)

    return pd.DataFrame()


# -------------------------------------------------------------------
# Processed Dataset
# -------------------------------------------------------------------
def load_processed_data():

    if PROCESSED_DATA.exists():

        df = pd.read_parquet(PROCESSED_DATA)

        # -------------------------------
        # Sample data for dashboard
        # -------------------------------
        if len(df) > 50000:
            df = df.sample(
                n=50000,
                random_state=42
            )

        if "tstp" in df.columns:
            df["tstp"] = pd.to_datetime(df["tstp"])

        return df

    return pd.DataFrame()
# -------------------------------------------------------------------
# Individual outputs
# -------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_forecast_comparison():
    return load_csv("forecast_model_comparison.csv")


@st.cache_data(show_spinner=False)
def load_forecast_sample():
    df = load_csv("forecast_sample.csv")

    if not df.empty:
        df["tstp"] = pd.to_datetime(df["tstp"])

    return df


@st.cache_data(show_spinner=False)
def load_feature_importance():
    return load_csv("feature_importance.csv")


@st.cache_data(show_spinner=False)
def load_anomalies():

    df = load_csv("anomalies_detected.csv")

    if not df.empty:
        df["tstp"] = pd.to_datetime(df["tstp"])

    return df


@st.cache_data(show_spinner=False)
def load_cluster_summary():
    return load_csv("cluster_summary.csv")


@st.cache_data(show_spinner=False)
def load_household_clusters():
    return load_csv("household_clusters.csv")


@st.cache_data(show_spinner=False)
def load_recommendations():
    return load_csv("recommendations.csv")


# -------------------------------------------------------------------
# Load Everything
# -------------------------------------------------------------------

def load_all_data():

    return {

        "processed": load_processed_data(),

        "forecast_comparison": load_forecast_comparison(),

        "forecast_sample": load_forecast_sample(),

        "feature_importance": load_feature_importance(),

        "anomalies": load_anomalies(),

        "cluster_summary": load_cluster_summary(),

        "clusters": load_household_clusters(),

        "recommendations": load_recommendations(),
    }


# -------------------------------------------------------------------
# Dashboard KPIs
# -------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def dashboard_metrics():

    data = load_all_data()

    processed = data["processed"]

    rec = data["recommendations"]

    anomalies = data["anomalies"]

    forecast = data["forecast_comparison"]

    metrics = {}

    metrics["records"] = len(processed)

    metrics["households"] = (
        processed["LCLid"].nunique()
        if not processed.empty
        else 0
    )

    metrics["anomalies"] = len(anomalies)

    metrics["monthly_savings"] = (
        rec["monthly_savings_gbp"].sum()
        if not rec.empty
        else 0
    )

    metrics["avg_consumption"] = (
        processed["consumption"].mean()
        if not processed.empty
        else 0
    )

    metrics["forecast_model"] = ""

    metrics["forecast_r2"] = 0

    if not forecast.empty:

        best = forecast.sort_values("R2", ascending=False).iloc[0]

        metrics["forecast_model"] = best["Model"]

        metrics["forecast_r2"] = best["R2"]

    return metrics


# -------------------------------------------------------------------
# Household List
# -------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def household_ids():

    processed = load_processed_data()

    if processed.empty:
        return []

    return sorted(processed["LCLid"].unique())


# -------------------------------------------------------------------
# Filter Household
# -------------------------------------------------------------------

def household_data(household):

    df = load_processed_data()

    if df.empty:
        return df

    return df[df["LCLid"] == household].copy()


# -------------------------------------------------------------------
# Recommendation
# -------------------------------------------------------------------

def recommendation(household):

    df = load_recommendations()

    if df.empty:
        return pd.DataFrame()

    return df[df["LCLid"] == household]
