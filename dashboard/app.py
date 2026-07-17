"""
app.py
-------
Autonomous Energy Optimization Platform Dashboard

Author: Rushindra Dobila
"""

import streamlit as st

from styles import (
    load_css,
    hero,
    section,
    metric_card,
    workflow_card,
    recommendation_card,
    about_card,
    footer,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    WARNING,
    DANGER,
    INFO,
)

from data_loader import (
    load_all_data,
    dashboard_metrics,
)

from charts import *
from prediction import energy_advisor

# =====================================================
# Streamlit Config
# =====================================================

st.set_page_config(
    page_title="Autonomous Energy Optimization Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# Load CSS Style Overrides
# =====================================================

load_css()

# =====================================================
# Load Data
# =====================================================

data = load_all_data()
processed = data["processed"]

# Sample processed dataset for visualization
if not processed.empty and len(processed) > 20000:
    processed = processed.sample(n=20000, random_state=42)

forecast_df = data["forecast_comparison"]
forecast_sample = data["forecast_sample"]

# Sample forecast data
if not forecast_sample.empty and len(forecast_sample) > 10000:
    forecast_sample = forecast_sample.sample(n=10000, random_state=42)

feature_df = data["feature_importance"]
anomaly_df = data["anomalies"]

# Sample anomaly data
if not anomaly_df.empty and len(anomaly_df) > 10000:
    anomaly_df = anomaly_df.sample(n=10000, random_state=42)

cluster_summary = data["cluster_summary"]
cluster_df = data["clusters"]
recommendation_df = data["recommendations"]

# Sample recommendations
if not recommendation_df.empty and len(recommendation_df) > 5000:
    recommendation_df = recommendation_df.sample(n=5000, random_state=42)

metrics = dashboard_metrics()

# =====================================================
# Sidebar Navigation and Custom Widgets
# =====================================================

st.sidebar.markdown(
    """
    <div style="padding: 10px 0; text-align: center;">
        <h2 style="color: white !important; font-size: 22px; font-weight: 800; margin: 0; letter-spacing: 0.5px;">⚡ Energy Console</h2>
        <p style="color: #94A3B8 !important; font-size: 11px; margin: 5px 0 0 0;">Autonomous Optimization Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation System",
    [
        "🏠 Home",
        "📊 Analytics",
        "🤖 AI Advisor",
        "⚙ Workflow",
        "ℹ About",
    ]
)

st.sidebar.markdown("---")

# Render Custom Sidebar KPI metrics with high-contrast, beautiful widgets
st.sidebar.markdown(
    f"""
    <div style="margin-top: 15px;">
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">📁 Total Records</div>
            <div class="sidebar-metric-value">{metrics['records']:,}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">🏠 Households</div>
            <div class="sidebar-metric-value">{metrics['households']}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">🚨 Detected Anomalies</div>
            <div class="sidebar-metric-value">{metrics['anomalies']}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">🧠 Best Forecast Model</div>
            <div class="sidebar-metric-value" style="font-size: 14px; white-space: normal; line-height: 1.3;">{metrics['forecast_model']}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# HOME PAGE
# =====================================================

if page == "🏠 Home":
    hero()

    section(
        "Dashboard Overview",
        "Key performance indicators aggregated from the machine learning pipeline."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Records",
            f"{metrics['records']:,}",
            "Processed meter readings",
            icon="📁",
            color=PRIMARY
        )

    with c2:
        metric_card(
            "Households",
            str(metrics["households"]),
            "Unique households analyzed",
            icon="🏠",
            color=INFO
        )

    with c3:
        metric_card(
            "Detected Anomalies",
            str(metrics["anomalies"]),
            "Isolation Forest pipeline",
            icon="🚨",
            color=DANGER
        )

    with c4:
        metric_card(
            "Best Forecast Model",
            metrics["forecast_model"],
            f"Cross-Validation R² = {metrics['forecast_r2']:.3f}",
            icon="🧠",
            color=SUCCESS
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    section(
        "Dataset Overview",
        "Frequency distribution of energy consumption metrics."
    )

    st.plotly_chart(
        consumption_distribution(processed),
        use_container_width=True
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    section(
        "Forecast Performance",
        "Accuracy metrics and model comparison matrices."
    )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            forecast_model_chart(forecast_df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            r2_chart(forecast_df),
            use_container_width=True
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    section(
        "Feature Importance Analysis",
        "Top predictive variables influencing energy forecasting."
    )

    st.plotly_chart(
        top_feature_chart(feature_df),
        use_container_width=True
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    section(
        "Savings Opportunities",
        "Top households ranked by maximum potential monthly savings."
    )

    st.plotly_chart(
        savings_chart(recommendation_df),
        use_container_width=True
    )

    footer()

# =====================================================
# ANALYTICS PAGE
# =====================================================

elif page == "📊 Analytics":
    section(
        "Advanced Analytics Console",
        "Deep-dive analysis of forecasting accuracies, cluster segmentations, anomaly distributions, and optimization metrics."
    )

    # -------------------------------------------------
    # Forecasting
    # -------------------------------------------------
    st.subheader("📈 Energy Consumption Forecasting")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            forecast_model_chart(forecast_df),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            rmse_chart(forecast_df),
            use_container_width=True,
        )

    st.plotly_chart(
        radar_chart(forecast_df),
        use_container_width=True,
    )

    st.plotly_chart(
        metric_table(forecast_df),
        use_container_width=True,
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Actual vs Prediction
    # -------------------------------------------------
    st.subheader("📉 Actual vs Predicted Consumption")

    household = st.selectbox(
        "Select Household for Forecast Plot",
        sorted(forecast_sample["LCLid"].unique())
        if not forecast_sample.empty
        else [],
        key="forecast_household",
    )

    if household:
        st.plotly_chart(
            actual_vs_prediction(
                forecast_sample,
                household,
            ),
            use_container_width=True,
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Feature Importance
    # -------------------------------------------------
    st.subheader("🎯 Feature Importance Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            feature_importance_chart(feature_df),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            top_feature_chart(feature_df),
            use_container_width=True,
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Anomaly Detection
    # -------------------------------------------------
    st.subheader("🚨 Anomaly Detection Profile")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            anomaly_severity_chart(anomaly_df),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            top_anomaly_households(anomaly_df),
            use_container_width=True,
        )

    st.plotly_chart(
        anomaly_timeline(anomaly_df),
        use_container_width=True,
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Clustering
    # -------------------------------------------------
    st.subheader("🏠 Household Behavioral Clustering")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            cluster_distribution(cluster_df),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            cluster_average_consumption(cluster_summary),
            use_container_width=True,
        )

    st.plotly_chart(
        peak_ratio_chart(cluster_summary),
        use_container_width=True,
    )

    st.plotly_chart(
        weekend_weekday_chart(cluster_summary),
        use_container_width=True,
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Household Load Curve
    # -------------------------------------------------
    st.subheader("⚡ Household Daily Load Curves")

    selected_house = st.selectbox(
        "Select Household for Average Load Curve",
        sorted(cluster_df["LCLid"].unique())
        if not cluster_df.empty
        else [],
        key="cluster_household",
    )

    if selected_house:
        st.plotly_chart(
            load_curve(
                cluster_df,
                selected_house,
            ),
            use_container_width=True,
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------
    st.subheader("💡 Energy Saving & Cohort Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            recommendation_chart(recommendation_df),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            savings_chart(recommendation_df),
            use_container_width=True,
        )

    st.plotly_chart(
        savings_table(recommendation_df),
        use_container_width=True,
    )

    footer()

# =====================================================
# AI ENERGY ADVISOR
# =====================================================

elif page == "🤖 AI Advisor":
    section(
        "AI Energy Advisor Engine",
        "Identify anomalous trends, analyze cluster cohorts, and view savings strategies tailored per smart meter node."
    )

    energy_advisor()
    footer()

# =====================================================
# WORKFLOW
# =====================================================

elif page == "⚙ Workflow":
    section(
        "Machine Learning Pipeline Flow",
        "A visualization of the pipeline architecture from smart telemetry ingest to final support recommendations."
    )

    # Cohesive Horizontal Timeline Layout
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    # Row 1: Steps 1 to 4
    row1 = st.columns(4)
    with row1[0]:
        workflow_card(
            "1",
            "Data Collection",
            "London Smart Meter dataset ingestion, quality validation, and database load.",
            has_next=True
        )

    with row1[1]:
        workflow_card(
            "2",
            "Feature Engineering",
            "Generates statistical aggregates, temporal calendars, and meteorological variables.",
            has_next=True
        )

    with row1[2]:
        workflow_card(
            "3",
            "Forecasting Models",
            "Runs regression models (XGBoost, Random Forests) to forecast consumption timelines.",
            has_next=True
        )

    with row1[3]:
        workflow_card(
            "4",
            "Anomaly Detection",
            "Executes unsupervised Isolation Forests to flag out-of-bounds power surges.",
            has_next=False
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Row 2: Steps 5 to 8
    row2 = st.columns(4)
    with row2[0]:
        workflow_card(
            "5",
            "K-Means Clustering",
            "Segments consumer nodes based on hourly load behaviors into behavioral profiles.",
            has_next=True
        )

    with row2[1]:
        workflow_card(
            "6",
            "Recommendation Engine",
            "Maps cluster patterns and savings potential into explicit consumer recommendation cards.",
            has_next=True
        )

    with row2[2]:
        workflow_card(
            "7",
            "Dashboard Services",
            "Exposes analytical variables, timelines, and metrics through a Streamlit UI portal.",
            has_next=True
        )

    with row2[3]:
        workflow_card(
            "8",
            "Optimization Support",
            "Empowers residential managers to plan demand responses and control grid load peaks.",
            has_next=False
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Core Technology Stack")

    tech1, tech2, tech3 = st.columns(3)

    with tech1:
        st.info(
            """
**Machine Learning Algorithms**

- **XGBoost Regressor**: Energy forecasting
- **Random Forest**: consumption estimations
- **Linear Regression**: Baseline computations
- **Isolation Forest**: Usage anomaly detection
- **K-Means Clustering**: Behavioral profiling
            """
        )

    with tech2:
        st.info(
            """
**Core Python Libraries**

- **Pandas**: Data transformation and cleaning
- **NumPy**: Vectorized mathematics
- **Scikit-Learn**: Cluster and anomaly training
- **Plotly Express**: Interactive chart generation
- **Streamlit**: Application runtime rendering
            """
        )

    with tech3:
        st.info(
            """
**Platform Features**

- Time-series energy forecasting
- Automatic usage spike alert rules
- Dynamic household profiling cohorts
- Custom savings calculations (£/mo)
- Modern administrative metrics console
            """
        )

    footer()

# =====================================================
# ABOUT
# =====================================================

elif page == "ℹ About":
    section(
        "About the Project",
        "Autonomous Energy Optimization Platform Details"
    )

    # Refactored plain markdown into visually stunning HTML cards
    col1, col2 = st.columns(2)

    with col1:
        about_card(
            "Project Objective",
            "⚡",
            """
            <p>
            The <strong>Autonomous Energy Optimization Platform</strong> is an enterprise-grade AI decision support system 
            trained and validated on the <strong>London Smart Meter Dataset</strong>.
            </p>
            <p>
            By integrating time-series regression forecasting, behavioral segmentation, and unsupervised anomaly detection, 
            the platform transforms dense power grids data into clear savings recommendations for residential consumers.
            </p>
            """,
            border_color=PRIMARY
        )

        about_card(
            "Dataset Metadata",
            "📊",
            """
            <p><strong>London Smart Meter Dataset (UK Power Networks)</strong></p>
            <p>
            Consists of half-hourly electrical consumption logs (kWh) for thousands of London households over multiple years. 
            The records are mapped against:
            </p>
            <ul>
                <li>Localized DarkSky API meteorological conditions</li>
                <li>UK government bank holidays and weekend indicators</li>
                <li>ACORN demographic classifications</li>
            </ul>
            """,
            border_color=INFO
        )

    with col2:
        about_card(
            "Machine Learning Infrastructure",
            "🧠",
            """
            <p><strong>Forecasting Suite</strong></p>
            <ul>
                <li>XGBoost & Random Forest regression models trained on historic load profiles.</li>
            </ul>
            <p><strong>Anomaly Detection Pipeline</strong></p>
            <ul>
                <li>Isolation Forest architectures profiling consumption data to flag severe spike anomalies.</li>
            </ul>
            <p><strong>Household Cohorts Segmentation</strong></p>
            <ul>
                <li>K-Means clustering categorizing households by load curve, peak ratios, and weekend habits.</li>
            </ul>
            """,
            border_color=SUCCESS
        )

        about_card(
            "Technology Architecture",
            "⚙️",
            """
            <ul>
                <li><strong>Programming Language</strong>: Python 3.10+</li>
                <li><strong>Data Processing</strong>: Pandas, NumPy, PyArrow Parquet</li>
                <li><strong>Modeling Engine</strong>: Scikit-Learn, XGBoost</li>
                <li><strong>Visualizations</strong>: Plotly Vector Graphics engine</li>
                <li><strong>Platform GUI</strong>: Streamlit Framework</li>
            </ul>
            """,
            border_color=WARNING
        )

    st.markdown("---")
    
    dev_col1, dev_col2 = st.columns([1, 2])
    
    with dev_col1:
        about_card(
            "Developer Profile",
            "👤",
            """
            <p style="font-weight: 700; font-size: 16px; margin: 0; color: #0F172A;">Rushindra Dobila</p>
            <p style="color: #64748B; margin-top: 4px;">B.Tech Computer Science Engineering</p>
            <p style="font-size: 13px; margin: 8px 0 0 0;">
                Specialization: Artificial Intelligence & Machine Learning<br>
                Graduation: 2026
            </p>
            <p style="margin-top: 12px;">
                <a href="https://github.com" target="_blank" class="stButton" style="display:inline-block; padding: 6px 12px; background:#2563EB; color:white !important; text-decoration:none; border-radius: 8px; font-weight:600; font-size:12px;">View GitHub Portfolio</a>
            </p>
            """,
            border_color=SECONDARY
        )
        
    with dev_col2:
        about_card(
            "Platform Capabilities Summary",
            "🎓",
            """
            <p>
            This system serves as a B.Tech Major Graduation Project. It provides grid operators and energy advisors 
            with full-scope dashboard insights to:
            </p>
            <ul>
                <li>Track and schedule power allocations based on accurate forecasted consumption limits.</li>
                <li>Detect and research node anomalies to locate possible meter issues or line leakages.</li>
                <li>Analyze household profiles to offer bespoke peak-hours rate incentives.</li>
            </ul>
            """,
            border_color=PRIMARY
        )

    footer()