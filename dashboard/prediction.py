"""
prediction.py
-------------
AI Energy Advisor
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# =====================================================
# Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# =====================================================
# Load Data
# =====================================================

@st.cache_data
def load_recommendations():
    return pd.read_csv(OUTPUT_DIR / "recommendations.csv")


@st.cache_data
def load_clusters():
    return pd.read_csv(OUTPUT_DIR / "household_clusters.csv")


@st.cache_data
def load_cluster_summary():
    return pd.read_csv(OUTPUT_DIR / "cluster_summary.csv")


@st.cache_data
def load_forecast():
    return pd.read_csv(OUTPUT_DIR / "forecast_sample.csv")


@st.cache_data
def load_anomalies():
    return pd.read_csv(OUTPUT_DIR / "anomalies_detected.csv")


recommendations = load_recommendations()
clusters = load_clusters()
cluster_summary = load_cluster_summary()
forecast = load_forecast()
anomalies = load_anomalies()

# =====================================================
# Household List
# =====================================================

def household_list():
    """Return households that have data in recommendations AND clusters."""
    rec_ids   = set(recommendations["LCLid"].unique())
    clust_ids = set(clusters["LCLid"].unique())
    valid_ids = rec_ids & clust_ids
    return sorted(list(valid_ids))


# =====================================================
# Forecast Information
# =====================================================

def forecast_information(household):
    df = forecast[forecast["LCLid"] == household]

    if df.empty:
        # Forecast sample doesn't cover every household — return safe defaults
        return {
            "actual":    0.0,
            "predicted": 0.0,
            "minimum":   0.0,
            "maximum":   0.0,
        }

    return {
        "actual":    round(df["consumption"].mean(), 3),
        "predicted": round(df["predicted"].mean(), 3),
        "minimum":   round(df["consumption"].min(), 3),
        "maximum":   round(df["consumption"].max(), 3),
    }

# =====================================================
# Cluster Information
# =====================================================

def cluster_information(household):
    row = clusters[clusters["LCLid"] == household]

    if row.empty:
        return None

    cluster = row.iloc[0]["cluster"]

    summary = cluster_summary[
        cluster_summary["cluster"] == cluster
    ]

    if summary.empty:
        return None

    return summary.iloc[0]

# =====================================================
# Savings Information
# =====================================================

def savings_information(household):
    row = recommendations[
        recommendations["LCLid"] == household
    ]

    if row.empty:
        return None

    row = row.iloc[0]

    return {
        "monthly": round(row["monthly_savings_gbp"], 2),
        "pattern": row["usage_pattern"],
        "recommendation": row["recommendation"],
    }

# =====================================================
# Anomaly Information
# =====================================================

def anomaly_information(household):
    df = anomalies[
        anomalies["LCLid"] == household
    ]

    if df.empty:
        return {
            "count": 0,
            "risk": "Low"
        }

    count = len(df)

    if count > 200:
        risk = "High"
    elif count > 50:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "count": count,
        "risk": risk
    }

# =====================================================
# UI Helper Functions
# =====================================================

def result_card(title, value, unit="", color="#2563EB", icon="📊"):
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 20px;
            border-left: 6px solid {color};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 12px;
            transition: all 0.3s ease;
        ">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 16px;">{icon}</span>
                <span style="font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">{title}</span>
            </div>
            <div style="font-size: 26px; font-weight: 700; color: #0F172A;">
                {value} <span style="font-size: 16px; font-weight: 500; color: #64748B;">{unit}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_box(text):

    st.markdown(
        f"""
        <div style="
            background: #EFF6FF;
            border: 1px solid #3B82F640;
            border-left: 6px solid #2563EB;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            height: 100%;
        ">
            <div style="font-size: 12px; font-weight: 600; color: #2563EB; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                💡 AI Energy Optimization Advice
            </div>
            <div style="color: #1E3A8A; font-size: 15px; line-height: 1.6; font-weight: 500;">
                {text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_box(level):
    colors = {
        "Low": {"bg": "#F0FDF4", "border": "#22C55E", "text": "#166534", "icon": "✅"},
        "Medium": {"bg": "#FFFBEB", "border": "#F59E0B", "text": "#92400E", "icon": "⚠️"},
        "High": {"bg": "#FEF2F2", "border": "#EF4444", "text": "#991B1B", "icon": "🚨"},
    }
    info = colors.get(level, {"bg": "#F8FAFC", "border": "#64748B", "text": "#1E293B", "icon": "ℹ️"})
    st.markdown(
        f"""
        <div style="
            background: {info['bg']};
            border: 1px solid {info['border']}40;
            border-left: 6px solid {info['border']};
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            height: 100%;
        ">
            <div style="font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                {info['icon']} Consumption Risk Assessment
            </div>
            <h4 style="margin: 0; color: #475569; font-size: 14px; font-weight: 500;">Anomaly Risk Level</h4>
            <div style="color: {info['text']}; font-size: 32px; font-weight: 800; margin-top: 8px; display: flex; align-items: center; gap: 8px;">
                {level}
            </div>
            <p style="margin: 8px 0 0 0; font-size: 12px; color: #64748B;">Based on frequency and severity of out-of-bounds usage.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def profile_card(cluster_id, label, avg_consumption, peak_ratio):
    st.markdown(
        f"""
        <div class="advisor-card">
            <div class="advisor-card-header">👥 Household Clustering Profile</div>
            <div class="advisor-grid">
                <div class="advisor-item">
                    <div class="advisor-label">K-Means Cluster</div>
                    <div class="advisor-val">#{cluster_id}</div>
                </div>
                <div class="advisor-item">
                    <div class="advisor-label">Behavior Classification</div>
                    <div class="advisor-val" style="font-size: 15px; margin-top: 10px; font-weight: 700; color: #2563EB;">{label}</div>
                </div>
                <div class="advisor-item">
                    <div class="advisor-label">Cluster Avg Usage</div>
                    <div class="advisor-val">{avg_consumption:.3f} <span style="font-size: 12px; font-weight: 500; color: #64748B;">kWh</span></div>
                </div>
                <div class="advisor-item">
                    <div class="advisor-label">Peak to Average</div>
                    <div class="advisor-val">{peak_ratio:.2f}x</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def forecast_summary_card(min_val, avg_val, max_val):
    st.markdown(
        f"""
        <div class="advisor-card">
            <div class="advisor-card-header">📈 Forecasted Consumption Limits</div>
            <div class="advisor-grid">
                <div class="advisor-item" style="border-bottom: 4px solid #16A34A;">
                    <div class="advisor-label">Minimum Consumption</div>
                    <div class="advisor-val">{min_val:.3f} <span style="font-size: 12px; font-weight: 500; color: #64748B;">kWh</span></div>
                </div>
                <div class="advisor-item" style="border-bottom: 4px solid #2563EB;">
                    <div class="advisor-label">Average Consumption</div>
                    <div class="advisor-val">{avg_val:.3f} <span style="font-size: 12px; font-weight: 500; color: #64748B;">kWh</span></div>
                </div>
                <div class="advisor-item" style="border-bottom: 4px solid #DC2626;">
                    <div class="advisor-label">Maximum Consumption</div>
                    <div class="advisor-val">{max_val:.3f} <span style="font-size: 12px; font-weight: 500; color: #64748B;">kWh</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def usage_pattern_card(pattern):
    st.markdown(
        f"""
        <div class="advisor-card" style="border-left: 6px solid #8B5CF6;">
            <div class="advisor-card-header" style="color: #6D28D9 !important; font-size: 16px; margin-bottom: 8px;">
                ⚡ Behavioral Usage Pattern
            </div>
            <div style="font-size: 15px; color: #4C1D95; font-weight: 500; line-height: 1.6;">
                {pattern}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================
# Main AI Energy Advisor
# =====================================================

def energy_advisor():
    st.markdown(
        """
        Select a household to view AI-powered energy insights,
        forecast information, savings, anomalies, and recommendations.
        """
    )

    households = household_list()

    if len(households) == 0:
        st.warning("No households available.")
        return

    household = st.selectbox(
        "🏠 Select Household ID",
        households
    )

    # -------------------------------------------------
    # Load Household Data
    # -------------------------------------------------

    forecast_info = forecast_information(household)
    cluster_info = cluster_information(household)
    saving_info = savings_information(household)
    anomaly_info = anomaly_information(household)

    if (
        forecast_info is None
        or cluster_info is None
        or saving_info is None
        or anomaly_info is None
    ):
        st.error("Unable to load household information.")
        return

    # -------------------------------------------------
    # Household ID Banner
    # -------------------------------------------------
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1E3A8A, #2563EB);
            border-radius: 14px;
            padding: 16px 22px;
            margin: 16px 0;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 22px;">🏠</span>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 1px;">Selected Household ID</div>
                <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.5px; margin-top: 2px;">{household}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    c1, c2, c3, c4 = st.columns(4)

    with c1:
        result_card(
            "Average Consumption",
            forecast_info["actual"],
            "kWh",
            "#2563EB",
            "📊"
        )

    with c2:
        result_card(
            "Predicted Consumption",
            forecast_info["predicted"],
            "kWh",
            "#16A34A",
            "📈"
        )

    with c3:
        result_card(
            "Monthly Savings",
            saving_info["monthly"],
            "£",
            "#0EA5E9",
            "💰"
        )

    with c4:
        result_card(
            "Detected Anomalies",
            anomaly_info["count"],
            "events",
            "#DC2626" if anomaly_info["count"] > 50 else "#F59E0B",
            "🚨"
        )

    # -------------------------------------------------
    # Household Profile
    # -------------------------------------------------

    st.divider()

    profile_card(
        int(cluster_info["cluster"]),
        cluster_info["label"],
        cluster_info["avg_consumption"],
        cluster_info["peak_to_avg_ratio"]
    )

    # -------------------------------------------------
    # Risk & Recommendation
    # -------------------------------------------------

    st.divider()

    left, right = st.columns(2)

    with left:
        risk_box(
            anomaly_info["risk"]
        )

    with right:
        recommendation_box(
            saving_info["recommendation"]
        )

    # -------------------------------------------------
    # Forecast Summary
    # -------------------------------------------------

    st.divider()

    forecast_summary_card(
        forecast_info["minimum"],
        forecast_info["actual"],
        forecast_info["maximum"]
    )

    # -------------------------------------------------
    # Usage Pattern
    # -------------------------------------------------

    st.divider()

    usage_pattern_card(
        saving_info["pattern"]
    )

    # -------------------------------------------------
    # Download Report
    # -------------------------------------------------

    st.divider()

    report = pd.DataFrame({
        "Household": [household],
        "Average Consumption (kWh)": [forecast_info["actual"]],
        "Predicted Consumption (kWh)": [forecast_info["predicted"]],
        "Monthly Savings (£)": [saving_info["monthly"]],
        "Cluster": [cluster_info["label"]],
        "Risk Level": [anomaly_info["risk"]],
        "Recommendation": [saving_info["recommendation"]],
    })

    st.download_button(
        "📥 Download Household Report (CSV)",
        data=report.to_csv(index=False),
        file_name=f"{household}_report.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    energy_advisor()
