"""
pipeline.py
-----------
Master orchestration pipeline for the Autonomous Energy Optimization Platform.

Workflow

1. Load & preprocess smart meter data
2. Forecast energy consumption
3. Detect anomalies
4. Cluster households
5. Generate recommendations

Outputs are written to:
    data/
    outputs/

Dashboard reads directly from these outputs.
"""

from pathlib import Path
import logging
import time

import data_pipeline
import forecasting
import anomaly_detection
import clustering
import recommendations

# --------------------------------------------------------
# Logging
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)

logger = logging.getLogger("EnergyPipeline")

# --------------------------------------------------------
# Paths
# --------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------
# Helper
# --------------------------------------------------------


def log_stage(stage_name, start_time):
    elapsed = time.time() - start_time
    logger.info(f"{stage_name} completed in {elapsed:.2f} seconds")


# --------------------------------------------------------
# Main Pipeline
# --------------------------------------------------------

def main(
    n_blocks=None,
    save_processed=True,
):
    """
    Runs the complete Energy Optimization pipeline.

    Parameters
    ----------
    n_blocks : int or None

        Number of block CSVs to load.

        None -> load all.

    save_processed : bool

        Save processed parquet file.

    Returns
    -------
    dict
    """

    pipeline_start = time.time()

    logger.info("=" * 70)
    logger.info("AUTONOMOUS ENERGY OPTIMIZATION PIPELINE")
    logger.info("=" * 70)

    try:

        # --------------------------------------------------
        # STEP 1
        # --------------------------------------------------

        logger.info("STEP 1 : DATA PIPELINE")

        t = time.time()

        df = data_pipeline.run_pipeline(
            n_blocks=n_blocks,
            save=save_processed,
        )

        if df.empty:
            raise ValueError("Processed dataframe is empty.")

        logger.info(f"Rows       : {len(df):,}")
        logger.info(f"Households : {df['LCLid'].nunique():,}")

        log_stage("Data Pipeline", t)

        # --------------------------------------------------
        # STEP 2
        # --------------------------------------------------

        logger.info("STEP 2 : FORECASTING")

        t = time.time()

        forecast_model, forecast_results = forecasting.run_forecasting(df)

        log_stage("Forecasting", t)

        # --------------------------------------------------
        # STEP 3
        # --------------------------------------------------

        logger.info("STEP 3 : ANOMALY DETECTION")

        t = time.time()

        df, anomalies = anomaly_detection.run_anomaly_detection(df)

        logger.info(f"Detected anomalies : {len(anomalies):,}")

        log_stage("Anomaly Detection", t)

        # --------------------------------------------------
        # STEP 4
        # --------------------------------------------------

        logger.info("STEP 4 : HOUSEHOLD CLUSTERING")

        t = time.time()

        household_clusters, cluster_summary = clustering.run_clustering(df)

        logger.info(
            f"Clusters created : {cluster_summary.shape[0]}"
        )

        log_stage("Clustering", t)

        # --------------------------------------------------
        # STEP 5
        # --------------------------------------------------

        logger.info("STEP 5 : RECOMMENDATION ENGINE")

        t = time.time()

        recommendations_df = recommendations.generate_recommendations(
            df=df,
            anomalies=anomalies,
            fingerprints=household_clusters,
            cluster_summary=cluster_summary,
        )

        logger.info(
            f"Recommendations : {len(recommendations_df):,}"
        )

        log_stage("Recommendations", t)

        # --------------------------------------------------
        # FINISHED
        # --------------------------------------------------

        total_time = time.time() - pipeline_start

        logger.info("=" * 70)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)

        logger.info(f"Total execution time : {total_time:.2f} seconds")
        logger.info(f"Processed data saved : {DATA_DIR}")
        logger.info(f"Outputs saved        : {OUTPUT_DIR}")

        logger.info(
            "Run the dashboard using:\n"
            "streamlit run dashboard/app.py"
        )

        return {

            "processed_data": df,

            "forecast_results": forecast_results,

            "anomalies": anomalies,

            "household_clusters": household_clusters,

            "cluster_summary": cluster_summary,

            "recommendations": recommendations_df,

            "execution_time": total_time,
        }

    except Exception as e:

        logger.exception("Pipeline execution failed.")

        raise e


# --------------------------------------------------------
# Entry Point
# --------------------------------------------------------

if __name__ == "__main__":

    main(
        n_blocks=20,
        save_processed=True,
    )