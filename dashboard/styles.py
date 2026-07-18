"""
styles.py
---------
Custom styling for the Autonomous Energy Optimization Platform dashboard.
"""

import streamlit as st

# ==========================================================
# Consistent Color Palette
# ==========================================================
PRIMARY = "#2563EB"       # Primary Blue
SECONDARY = "#0F172A"     # Secondary Slate
SUCCESS = "#16A34A"       # Success Green
WARNING = "#F59E0B"       # Warning Amber
DANGER = "#DC2626"        # Danger Red
INFO = "#0EA5E9"          # Info Cyan
BACKGROUND = "#F1F5F9"    # Background Light Gray
CARD = "#FFFFFF"          # Card White


def load_css():
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---------- General ---------- */
html, body, [class*="css"], [class*="st-"] {{
    font-family: 'Inter', "Segoe UI", -apple-system, sans-serif !important;
    color: #0F172A !important;
}}

.stApp {{
    background-color: {BACKGROUND};
}}

/* Force light theme elements to have high contrast */
h1, h2, h3, h4, h5, h6 {{
    color: #0F172A !important;
    font-family: 'Inter', "Segoe UI", sans-serif !important;
    font-weight: 700 !important;
}}

p, span, label, li, ul, ol, div {{
    color: #334155;
    font-family: 'Inter', "Segoe UI", sans-serif;
}}

p {{
    font-size: 15px;
    line-height: 1.6;
}}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0F172A, #1E293B) !important;
    border-right: 1px solid #1E293B;
}}

/* Target specific sidebar text items to avoid leakage of collapse button texts */
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h2 {{
    color: #F8FAFC !important;
}}

/* Hide default streamlit radio buttons circles/dots */
section[data-testid="stSidebar"] div[role="radiogroup"] span[data-baseweb="radio"] {{
    display: none !important;
}}

/* Style the navigation links as professional menu tabs */
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    padding: 12px 18px !important;
    border-radius: 10px !important;
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    margin-bottom: 8px !important;
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
    transform: translateX(4px);
}}

/* Highlight selected menu tabs */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {{
    background: rgba(37, 99, 235, 0.2) !important;
    border-color: {PRIMARY} !important;
    border-left: 4px solid {PRIMARY} !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] * {{
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: #334155 !important;
}}

/* Sidebar Custom Metric Widgets */
.sidebar-metric {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid {PRIMARY};
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}}
.sidebar-metric-title {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94A3B8 !important;
    font-weight: 600;
}}
.sidebar-metric-value {{
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-top: 4px;
}}

/* ---------- Hero ---------- */
.hero {{
    background: linear-gradient(135deg, #1E3A8A, #2563EB);
    padding: 40px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
}}

.hero h1, .hero h2, .hero h3, .hero div, .hero span, .hero p, .hero small, .hero * {{
    color: #FFFFFF !important;
}}

.hero h1 {{
    font-size: 34px;
    font-weight: 800 !important;
    margin-bottom: 12px;
    color: #FFFFFF !important;
}}

.hero p {{
    font-size: 16px;
    opacity: 0.9;
    color: #E2E8F0 !important;
    line-height: 1.6;
    margin-bottom: 16px;
}}

.hero small {{
    display: inline-block;
    background: rgba(255, 255, 255, 0.1);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    color: #F1F5F9 !important;
    border: 1px solid rgba(255, 255, 255, 0.15);
}}

/* ---------- KPI Cards ---------- */
.metric-card {{
    background: {CARD};
    border-radius: 16px;
    padding: 22px;
    border-left: 6px solid {PRIMARY};
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 15px;
}}

.metric-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.03);
}}

.metric-header {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.metric-icon {{
    font-size: 18px;
    background: #F1F5F9;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
}}

.metric-title {{
    color: #475569 !important;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.metric-value {{
    font-size: 30px;
    font-weight: 700;
    color: #0F172A !important;
    margin-top: 8px;
    line-height: 1.1;
}}

.metric-sub {{
    color: #64748B !important;
    font-size: 12px;
    margin-top: 2px;
}}

/* ---------- Section Header ---------- */
.section-title {{
    font-size: 24px;
    font-weight: 700;
    color: #0F172A !important;
    margin-top: 25px;
    margin-bottom: 6px;
}}

.section-sub {{
    color: #64748B !important;
    font-size: 14px;
    margin-bottom: 12px;
}}

.section-divider {{
    height: 4px;
    width: 60px;
    background: {PRIMARY};
    border-radius: 2px;
    margin-bottom: 25px;
}}

/* ---------- Custom Advisor Cards ---------- */
.advisor-card {{
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    border: 1px solid #E2E8F0;
    margin-bottom: 20px;
}}

.advisor-card-header {{
    font-size: 18px;
    font-weight: 600;
    color: #0F172A !important;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.advisor-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}}

.advisor-item {{
    background: #F8FAFC;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    text-align: center;
}}

.advisor-label {{
    font-size: 12px;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}}

.advisor-val {{
    font-size: 22px;
    font-weight: 700;
    color: #0F172A !important;
    margin-top: 6px;
}}



/* ---------- About Page Cards ---------- */
.about-card {{
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid #E2E8F0;
    margin-bottom: 24px;
    height: 100%;
}}
.about-card-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 12px;
}}
.about-card-icon {{
    font-size: 24px;
}}
.about-card-title {{
    font-size: 18px;
    font-weight: 700;
    color: #0F172A !important;
}}
.about-card-content {{
    color: #334155 !important;
    font-size: 14px;
    line-height: 1.6;
}}
.about-card-content ul {{
    margin: 0;
    padding-left: 20px;
}}
.about-card-content li {{
    margin-bottom: 8px;
    color: #334155 !important;
}}

/* ---------- Tables and Dataframe ---------- */
[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
    background: white;
}}

/* ---------- Interactive Elements ---------- */
.stSelectbox div[data-baseweb="select"] {{
    border-radius: 10px !important;
    border-color: #E2E8F0 !important;
}}
.stButton>button {{
    width: 100%;
    border-radius: 10px !important;
    height: 42px !important;
    border: none !important;
    background-color: {PRIMARY} !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.15) !important;
}}
.stButton>button:hover {{
    background-color: #1D4ED8 !important;
    box-shadow: 0 4px 6px rgba(37, 99, 235, 0.25) !important;
    transform: translateY(-1px);
}}

/* ---------- Expander ---------- */
details {{
    border-radius: 10px !important;
    background: white !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    padding: 6px !important;
}}
summary {{
    font-weight: 600 !important;
    color: #0F172A !important;
}}

/* ---------- Footer ---------- */
.footer {{
    text-align: center;
    color: #64748B !important;
    padding: 30px 10px 10px 10px;
    border-top: 1px solid #E2E8F0;
    margin-top: 40px;
    font-size: 13px;
}}
.footer a {{
    color: {PRIMARY} !important;
    text-decoration: none;
    font-weight: 500;
}}
.footer a:hover {{
    text-decoration: underline;
}}

</style>
""",
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        """
<div class="hero">
    <h1>⚡ Autonomous Energy Optimization Platform</h1>
    <p>
        An enterprise-grade, AI-powered decision support system analyzing London Smart Meter data.
        Forecast consumption, identify anomalies, segment households, and view tailored 
        savings optimizations on a unified digital console.
    </p>
    <small>
        Dataset: London Smart Meter Dataset | Models: XGBoost, Random Forest, Isolation Forest, K-Means
    </small>
</div>
""",
        unsafe_allow_html=True,
    )


def section(title, subtitle=""):
    st.markdown(
        f"""
<div class="section-title">{title}</div>
<div class="section-sub">{subtitle}</div>
<div class="section-divider"></div>
""",
        unsafe_allow_html=True,
    )


def metric_card(title, value, subtitle="", icon="📊", color=PRIMARY):
    st.markdown(
        f"""
<div class="metric-card" style="border-left-color: {color};">
    <div class="metric-header">
        <span class="metric-icon">{icon}</span>
        <span class="metric-title">{title}</span>
    </div>
    <div class="metric-value">{value}</div>
    <div class="metric-sub">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )



def recommendation_card(
    household,
    pattern,
    savings,
    recommendation,
):
    st.markdown(
        f"""
<div class="rec-card" style="background: white; border-radius: 16px; padding: 22px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 6px solid {SUCCESS}; margin-bottom: 20px;">
    <div class="rec-title" style="font-size: 18px; font-weight: 700; color: #0F172A; margin-bottom: 12px;">
        🏠 {household}
    </div>
    <div class="rec-pattern" style="color: #64748B; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
        Usage Pattern
    </div>
    <b style="color: #0F172A; font-size: 15px;">{pattern}</b>
    <div style="margin-top: 12px;">
        <div class="rec-pattern" style="color: #64748B; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
            Estimated Monthly Savings
        </div>
        <div class="rec-saving" style="font-size: 28px; color: {SUCCESS}; font-weight: 700; margin-top: 4px;">
            £{savings:.2f}
        </div>
    </div>
    <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 16px 0;">
    <div style="color: #334155; font-size: 14px; line-height: 1.5;">
        {recommendation}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def about_card(title, icon, content_html, border_color=PRIMARY):
    import textwrap
    cleaned_html = textwrap.dedent(content_html).strip()
    st.markdown(
        f"""
<div class="about-card" style="border-top: 4px solid {border_color};">
    <div class="about-card-header">
        <span class="about-card-icon">{icon}</span>
        <span class="about-card-title">{title}</span>
    </div>
    <div class="about-card-content">
        {cleaned_html}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """
<div class="footer">
    <strong>Autonomous Energy Optimization Platform</strong> &nbsp;•&nbsp; Version 1.0.0
    <br>
    <span style="font-size: 11px; color: #94A3B8;">Built with Streamlit &nbsp;•&nbsp; Plotly &nbsp;•&nbsp; Scikit-Learn &nbsp;•&nbsp; XGBoost</span>
</div>
""",
        unsafe_allow_html=True,
    )