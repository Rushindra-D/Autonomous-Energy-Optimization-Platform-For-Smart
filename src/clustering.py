
"""
clustering.py
-------------
Household usage segmentation using KMeans.
"""

from pathlib import Path
import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Clustering")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def build_household_fingerprints(df):
    df = df.copy()

    df["half_hour_slot"] = (
        df["tstp"].dt.hour * 2 +
        (df["tstp"].dt.minute // 30)
    )

    load_shape = (
        df.groupby(["LCLid","half_hour_slot"])["consumption"]
        .mean()
        .unstack(fill_value=0)
    )

    load_shape.columns=[f"slot_{i}" for i in load_shape.columns]

    summary = (
        df.groupby("LCLid")
        .agg(
            avg_consumption=("consumption","mean"),
            median_consumption=("consumption","median"),
            std_consumption=("consumption","std"),
            min_consumption=("consumption","min"),
            max_consumption=("consumption","max"),
        )
    )

    summary["base_load"] = (
        df.groupby("LCLid")["consumption"]
        .quantile(0.10)
    )

    summary["peak_to_avg_ratio"] = (
        summary["max_consumption"] /
        summary["avg_consumption"].replace(0,np.nan)
    )

    weekend = (
        df.groupby(["LCLid","is_weekend"])["consumption"]
        .mean()
        .unstack(fill_value=0)
    )

    if 1 in weekend.columns:
        summary["weekend_usage"] = weekend[1]
    else:
        summary["weekend_usage"] = 0

    if 0 in weekend.columns:
        summary["weekday_usage"] = weekend[0]
    else:
        summary["weekday_usage"] = 0

    meta_cols=[]
    for c in ["Acorn_grouped","stdorToU"]:
        if c in df.columns:
            meta=df.groupby("LCLid")[c].first()
            summary[c]=meta
            meta_cols.append(c)

    fp = load_shape.join(summary)
    return fp.dropna(), meta_cols


def label_clusters(summary):
    labels=[]
    for _,r in summary.iterrows():
        if r.avg_consumption>summary.avg_consumption.quantile(.75):
            labels.append("High Consumption")
        elif r.base_load>summary.base_load.quantile(.75):
            labels.append("High Base Load")
        elif r.peak_to_avg_ratio>summary.peak_to_avg_ratio.quantile(.75):
            labels.append("Peak Hour Users")
        else:
            labels.append("Balanced Users")
    return labels


def run_clustering(df,n_clusters=4):
    logger.info("Building household fingerprints")

    fp,meta_cols = build_household_fingerprints(df)

    numeric = fp.select_dtypes(include=np.number).columns.tolist()

    scaler=StandardScaler()
    X=scaler.fit_transform(fp[numeric])

    score = silhouette_score(X, KMeans(n_clusters=n_clusters,
                                       random_state=42,
                                       n_init=10).fit_predict(X))
    logger.info("Silhouette Score: %.3f",score)

    model=KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    fp["cluster"]=model.fit_predict(X)

    summary=fp.groupby("cluster")[
        [
            "avg_consumption",
            "base_load",
            "peak_to_avg_ratio",
            "weekend_usage",
            "weekday_usage",
        ]
    ].mean()

    summary["households"]=fp.groupby("cluster").size()
    summary["label"]=label_clusters(summary)

    fp.to_csv(OUTPUT_DIR/"household_clusters.csv")
    summary.to_csv(OUTPUT_DIR/"cluster_summary.csv")

    logger.info("\n%s",summary)

    return fp,summary


if __name__=="__main__":
    df=pd.read_parquet(DATA_DIR/"processed_meter_data.parquet")
    run_clustering(df)
