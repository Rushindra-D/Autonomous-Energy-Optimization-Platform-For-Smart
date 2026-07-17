
"""
forecasting.py
--------------
Forecast next-period household electricity consumption using
a Naive baseline and XGBoost.
"""

from pathlib import Path
import logging

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from xgboost import XGBRegressor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("Forecasting")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

FEATURE_COLS = [
    "hour",
    "dayofweek",
    "is_weekend",
    "month",
    "quarter",
    "weekofyear",
    "is_holiday",
    "temperature",
    "humidity",
    "windSpeed",
    "pressure",
    "lag_48",
    "lag_336",
    "roll_mean_48",
    "roll_std_48",
]

TARGET = "consumption"


def mape(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = y_true > 0.01
    return np.mean(np.abs((y_true[mask]-y_pred[mask])/y_true[mask]))*100


def validate_columns(df):
    missing = [c for c in FEATURE_COLS+[TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def chronological_split(df, test_frac=0.2):
    cutoff = df["tstp"].quantile(1-test_frac)
    return df[df.tstp < cutoff], df[df.tstp >= cutoff]


def evaluate(name, y_true, pred):
    return {
        "Model": name,
        "MAE": round(mean_absolute_error(y_true,pred),4),
        "RMSE": round(np.sqrt(mean_squared_error(y_true,pred)),4),
        "MAPE": round(mape(y_true,pred),2),
        "R2": round(r2_score(y_true,pred),4)
    }


def run_forecasting(df):
    validate_columns(df)

    train,test = chronological_split(df)

    train = train.dropna(subset=FEATURE_COLS+[TARGET])
    test = test.dropna(subset=FEATURE_COLS+[TARGET])

    logger.info("Train rows: %s", len(train))
    logger.info("Test rows : %s", len(test))

    baseline = test["lag_48"].values
    actual = test[TARGET].values
    mask = ~np.isnan(baseline)

    results = [
        evaluate("Naive Baseline", actual[mask], baseline[mask])
    ]

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )

    X_train = train[FEATURE_COLS]
    y_train = train[TARGET]

    X_test = test[FEATURE_COLS]
    y_test = test[TARGET]

    logger.info("Training XGBoost...")
    model.fit(X_train,y_train)

    pred = model.predict(X_test)

    results.append(evaluate("XGBoost", y_test, pred))

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        OUTPUT_DIR/"forecast_model_comparison.csv",
        index=False
    )

    forecast = test.copy()
    forecast["predicted"] = pred

    forecast[[
        "LCLid",
        "tstp",
        "consumption",
        "predicted"
    ]].head(5000).to_csv(
        OUTPUT_DIR/"forecast_sample.csv",
        index=False
    )

    importance = (
        pd.DataFrame({
            "Feature": FEATURE_COLS,
            "Importance": model.feature_importances_
        })
        .sort_values("Importance", ascending=False)
    )

    importance.to_csv(
        OUTPUT_DIR/"feature_importance.csv",
        index=False
    )

    logger.info("\\n%s", results_df)

    return model, results_df


if __name__ == "__main__":
    df = pd.read_parquet(DATA_DIR/"processed_meter_data.parquet")
    run_forecasting(df)
