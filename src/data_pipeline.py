"""
Energy Optimization Platform
Memory Optimized ETL Pipeline

This pipeline processes a configurable subset of the London Smart Meter Dataset.

Author: Rushindra Dobila
"""

import gc
import logging
from pathlib import Path
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
HALFHOURLY_DIR = DATA_DIR / "halfhourly_dataset" / "halfhourly_dataset"
PROCESSED_FILE = DATA_DIR / "processed_meter_data.parquet"
HOUSEHOLD_FILE = DATA_DIR / "informations_households.csv"
WEATHER_FILE = DATA_DIR / "weather_hourly_darksky.csv"
HOLIDAY_FILE = DATA_DIR / "uk_bank_holidays.csv"

DEFAULT_BLOCKS = 20

def load_energy_data(n_blocks=DEFAULT_BLOCKS):
    logger.info("=" * 60)
    logger.info("Loading Energy Dataset")
    logger.info("=" * 60)
    files = sorted(HALFHOURLY_DIR.glob("block_*.csv"))
    total_blocks = len(files)
    logger.info("Found %d block files", total_blocks)
    
    if n_blocks is not None:
        files = files[:n_blocks]
        logger.info("Processing first %d block files", len(files))
    else:
        logger.info("Processing ALL block files")

    energy_frames = []
    for i, file in enumerate(files, start=1):
        logger.info("[%d/%d] Reading %s", i, len(files), file.name)
        df = pd.read_csv(file, low_memory=False)
        df["tstp"] = pd.to_datetime(df["tstp"])
        df["consumption"] = pd.to_numeric(
            df["energy(kWh/hh)"].astype(str).str.strip().replace("", np.nan),
            errors="coerce"
        )
        df.drop(columns=["energy(kWh/hh)"], inplace=True)
        energy_frames.append(df)
        logger.info("Rows Loaded : %d", len(df))

    logger.info("Concatenating %d dataframes...", len(energy_frames))
    energy = pd.concat(energy_frames, ignore_index=True)
    del energy_frames
    gc.collect()
    energy = energy.sort_values(["LCLid", "tstp"])
    logger.info("Total Rows : %d", len(energy))
    logger.info("Unique Households : %d", energy["LCLid"].nunique())
    return energy

def load_households():
    logger.info("Loading household metadata...")
    households = pd.read_csv(HOUSEHOLD_FILE)
    logger.info("Household rows : %d", len(households))
    return households

def load_weather():
    logger.info("Loading weather dataset...")
    weather = pd.read_csv(WEATHER_FILE, encoding="latin1")
    weather["time"] = pd.to_datetime(weather["time"])
    weather = weather.sort_values("time")
    logger.info("Weather records : %d", len(weather))
    return weather

def load_holidays():
    logger.info("Loading UK Bank Holidays...")
    holidays = pd.read_csv(HOLIDAY_FILE, encoding="latin1")
    holidays["Bank holidays"] = pd.to_datetime(holidays["Bank holidays"])
    logger.info("Holiday records : %d", len(holidays))
    return holidays

def merge_datasets(energy, households, weather, holidays):
    logger.info("=" * 60 + "\nMerging Datasets\n" + "=" * 60)
    logger.info("Merging household information...")
    df = energy.merge(households, on="LCLid", how="left")
    del energy
    gc.collect()
    logger.info("Rows after household merge : %d", len(df))

    logger.info("Preparing weather merge...")
    weather = weather.sort_values("time")
    df = df.sort_values("tstp")
    logger.info("Running merge_asof...")
    df = pd.merge_asof(
        df, weather, left_on="tstp", right_on="time",
        direction="nearest", tolerance=pd.Timedelta("1h")
    )
    del weather
    gc.collect()
    logger.info("Weather merged successfully.")

    logger.info("Generating holiday flag...")
    holiday_dates = set(holidays["Bank holidays"].dt.date)
    df["is_holiday"] = df["tstp"].dt.date.isin(holiday_dates).astype(int)
    del holidays
    gc.collect()
    logger.info("Holiday feature created.")
    return df

def clean_data(df):
    logger.info("=" * 60 + "\nCleaning Dataset\n" + "=" * 60)
    before = len(df)
    df = df.drop_duplicates(subset=["LCLid", "tstp"])
    logger.info("Duplicates Removed : %d", before - len(df))

    before = len(df)
    df = df[df["consumption"] >= 0]
    logger.info("Negative Values Removed : %d", before - len(df))

    logger.info("Interpolating missing values...")
    df["consumption"] = df.groupby("LCLid")["consumption"].transform(
        lambda s: s.interpolate(limit=4).ffill().bfill()
    )

    before = len(df)
    df = df.dropna(subset=["consumption"])
    logger.info("Remaining Rows : %d", len(df))
    logger.info("Rows Removed : %d", before - len(df))
    logger.info("Cleaning completed.")
    return df

def engineer_features(df):
    logger.info("=" * 60 + "\nFeature Engineering\n" + "=" * 60)
    logger.info("Creating calendar features...")
    df["hour"] = df["tstp"].dt.hour
    df["day"] = df["tstp"].dt.day
    df["dayofweek"] = df["tstp"].dt.dayofweek
    df["month"] = df["tstp"].dt.month
    df["quarter"] = df["tstp"].dt.quarter
    df["weekofyear"] = df["tstp"].dt.isocalendar().week.astype(int)
    df["year"] = df["tstp"].dt.year
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)

    logger.info("Creating time-of-day features...")
    df["is_morning"] = df["hour"].between(6, 11).astype(int)
    df["is_afternoon"] = df["hour"].between(12, 17).astype(int)
    df["is_evening"] = df["hour"].between(18, 22).astype(int)
    df["is_night"] = ((df["hour"] >= 23) | (df["hour"] <= 5)).astype(int)

    logger.info("Creating lag features...")
    grp = df.groupby("LCLid")["consumption"]
    df["lag_1"] = grp.shift(1)
    df["lag_48"] = grp.shift(48)
    df["lag_336"] = grp.shift(336)

    logger.info("Creating rolling statistics...")
    df["roll_mean_48"] = grp.transform(lambda x: x.rolling(window=48, min_periods=12).mean())
    df["roll_std_48"] = grp.transform(lambda x: x.rolling(window=48, min_periods=12).std())
    df["roll_min_48"] = grp.transform(lambda x: x.rolling(window=48, min_periods=12).min())
    df["roll_max_48"] = grp.transform(lambda x: x.rolling(window=48, min_periods=12).max())

    logger.info("Creating daily household statistics...")
    household_stats = df.groupby("LCLid")["consumption"].agg(
        household_mean="mean", household_std="std", household_min="min", household_max="max"
    ).reset_index()
    df = df.merge(household_stats, on="LCLid", how="left")
    logger.info("Feature engineering completed.")
    return df

def validate(df):
    logger.info("=" * 60 + "\nDATA VALIDATION\n" + "=" * 60)
    logger.info("Rows               : %d", len(df))
    logger.info("Columns            : %d", len(df.columns))
    logger.info("Unique Households  : %d", df["LCLid"].nunique())
    logger.info("Date Range         : %s --> %s", df["tstp"].min(), df["tstp"].max())
    logger.info("Consumption Mean   : %.3f", df["consumption"].mean())
    logger.info("Consumption Std    : %.3f", df["consumption"].std())
    logger.info("Missing Values")
    missing = df.isnull().sum()
    logger.info("\n%s", missing[missing > 0])
    logger.info("=" * 60)
    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    logger.info("Memory Usage : %.2f MB", memory_mb)
    logger.info("=" * 60)

def run_pipeline(n_blocks=DEFAULT_BLOCKS, save=True):
    logger.info("=" * 70 + "\nENERGY OPTIMIZATION ETL PIPELINE\n" + "=" * 70)
    logger.info("Configured Blocks : %s", n_blocks)

    energy = load_energy_data(n_blocks)
    households = load_households()
    weather = load_weather()
    holidays = load_holidays()
    logger.info("All datasets loaded successfully.")

    df = merge_datasets(energy, households, weather, holidays)
    del energy, households, weather, holidays
    gc.collect()
    logger.info("Merge completed.")

    df = clean_data(df)
    gc.collect()
    logger.info("Cleaning completed.")

    df = engineer_features(df)
    gc.collect()
    logger.info("Feature engineering completed.")

    df = df.sort_values(["LCLid", "tstp"]).reset_index(drop=True)
    validate(df)

    if save:
        logger.info("=" * 70 + "\nSaving Processed Dataset\n" + "=" * 70)
        df.to_parquet(PROCESSED_FILE, index=False)
        logger.info("Processed dataset saved successfully.\nOutput : %s", PROCESSED_FILE)

    logger.info("=" * 70 + "\nETL PIPELINE COMPLETED SUCCESSFULLY\n" + "=" * 70)
    return df

if __name__ == "__main__":
    run_pipeline()