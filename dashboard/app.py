import sys
from pathlib import Path

import streamlit as st
import pandas as pd


# --------------------------------------
# Project Root
# --------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------
# Dashboard Sections
# --------------------------------------

from sections.executive_overview import render as render_executive_overview
from sections.store_performance import render as render_store_performance
from sections.product_sales_intelligence import render as render_product_sales_intelligence
from sections.demand_forecast import render as render_demand_forecast
from sections.inventory_risk import render as render_inventory_risk
from sections.ai_business_recommendation import render as render_ai_business_recommendation


# --------------------------------------
# RetailIQ - Main Application
# --------------------------------------

st.set_page_config(
    page_title="RetailIQ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------
# Global Styling
# --------------------------------------

st.markdown("""
<style>

/* ======================================
   Application
====================================== */

.stApp {
    background: #f4f7fb;
}

.main .block-container {
    max-width: 1450px;
    padding: 1.2rem 2.5rem 3rem;
}


/* ======================================
   Sidebar
====================================== */

section[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 20% 5%,
            rgba(38, 137, 255, 0.14),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #06172f 0%,
            #082348 50%,
            #0b315e 100%
        );

    border-right: 1px solid rgba(80, 150, 220, 0.18);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
}

section[data-testid="stSidebar"] * {
    color: #eaf3ff;
}


/* ======================================
   Sidebar Brand
====================================== */

.sidebar-brand {
    padding: 10px 5px 22px;
    margin-bottom: 24px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
}

.sidebar-logo {
    width: 50px;
    height: 50px;
    border-radius: 15px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: linear-gradient(135deg, #16c7ff, #2878ff);

    color: white;

    font-size: 23px;
    font-weight: 800;

    box-shadow:
        0 10px 28px rgba(23,137,255,0.30),
        inset 0 1px 0 rgba(255,255,255,0.25);

    margin-bottom: 13px;
}

.sidebar-title {
    color: white !important;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.7px;
}

.sidebar-subtitle {
    color: #8eafd2 !important;
    font-size: 11px;
    margin-top: 5px;
}


/* ======================================
   Navigation Header
====================================== */

.nav-header {
    color: #77a5d2 !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 5px 4px 5px;
}

.nav-description {
    color: #577fa9 !important;
    font-size: 11px;
    margin: 0 4px 17px;
}


/* ======================================
   Navigation
====================================== */

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 7px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    border-radius: 13px !important;
    border: 1px solid transparent !important;

    padding: 10px 12px !important;
    margin: 0 !important;

    background: transparent !important;

    transition:
        background 0.2s ease,
        border 0.2s ease,
        transform 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(45,145,255,0.10) !important;
    border-color: rgba(75,165,255,0.18) !important;
    transform: translateX(2px);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    color: #b8d0e8 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(
        135deg,
        rgba(26,143,255,0.30),
        rgba(45,91,184,0.24)
    ) !important;

    border-color: rgba(70,165,255,0.38) !important;

    box-shadow:
        0 8px 22px rgba(0,0,0,0.18),
        inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    color: white !important;
    font-weight: 750 !important;
}


/* Hide native radio circle
   (several selectors so it works across Streamlit versions) */

section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child,
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child,
section[data-testid="stSidebar"] div[role="radiogroup"] label > span:first-child:empty {
    display: none !important;
}


/* ======================================
   Header
====================================== */

.retailiq-header {
    background: linear-gradient(135deg, #082348, #0c315f);

    border: 1px solid rgba(45,113,177,0.55);

    border-radius: 17px;

    padding: 14px 20px;

    box-shadow: 0 10px 30px rgba(5,29,58,0.16);
}

.header-row {
    display: flex;
    align-items: center;
    gap: 13px;
}

.header-logo {
    width: 45px;
    height: 45px;

    border-radius: 13px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: linear-gradient(135deg, #16c7ff, #2878ff);

    color: white;

    font-size: 21px;
    font-weight: 800;

    box-shadow: 0 8px 20px rgba(23,137,255,0.25);
}

.header-title {
    color: white;
    font-size: 25px;
    font-weight: 800;
    line-height: 1;
}

.header-subtitle {
    color: #9fc4e9;
    font-size: 12px;
    margin-top: 5px;
}


/* ======================================
   Store Selector
====================================== */

div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: #d5e1ed !important;
}


/* ======================================
   Section Container
   .executive-container      -> legacy HTML wrapper
   .st-key-executive-container -> st.container(key="executive-container")
====================================== */

.executive-container,
.st-key-executive-container {
    background: white;

    border: 1px solid #e0e8f2;

    border-radius: 22px;

    padding: 28px 30px 32px;

    box-shadow: 0 12px 35px rgba(25,55,90,0.08);
}

.section-kicker {
    color: #168cf0;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.7px;

    text-transform: uppercase;
}

.section-title {
    color: #102b4c;

    font-size: 29px;

    font-weight: 800;

    margin-top: 5px;
}

.section-question {
    color: #66809d;

    font-size: 15px;

    font-weight: 600;

    margin: 4px 0 22px;
}


/* ======================================
   KPI Cards
====================================== */

.kpi-card {
    border: 1px solid #e0e8f2;

    border-radius: 16px;

    padding: 19px 20px;

    min-height: 132px;

    box-shadow: 0 6px 20px rgba(25,55,90,0.05);
}

.kpi-revenue {
    border-top: 4px solid #19b9a5;
    background: linear-gradient(145deg, #f5fffc, white);
}

.kpi-units {
    border-top: 4px solid #2878ff;
    background: linear-gradient(145deg, #f5f9ff, white);
}

.kpi-products {
    border-top: 4px solid #8267f7;
    background: linear-gradient(145deg, #faf8ff, white);
}

.kpi-risk {
    border-top: 4px solid #ef6a79;
    background: linear-gradient(145deg, #fff7f8, white);
}

.kpi-icon {
    font-size: 22px;
    margin-bottom: 7px;
}

.kpi-label {
    color: #73849a;
    font-size: 12px;
    font-weight: 700;
}

.kpi-value {
    color: #102b4c;
    font-size: 28px;
    font-weight: 800;
    margin-top: 3px;
}

.kpi-risk-value {
    color: #d33147;
}

.kpi-note {
    color: #8a99aa;
    font-size: 11px;
    margin-top: 5px;
}


/* ======================================
   Charts
====================================== */

.chart-card {
    background: white;

    border: 1px solid #e0e8f2;

    border-radius: 16px;

    padding: 17px 18px 8px;

    box-shadow: 0 6px 20px rgba(25,55,90,0.05);
}

.chart-title {
    color: #102b4c;

    font-size: 16px;

    font-weight: 800;
}

.chart-subtitle {
    color: #8a99aa;

    font-size: 11px;

    margin-top: 3px;
}


/* ======================================
   Insight
====================================== */

.info-box {
    background: linear-gradient(135deg, #eaf6ff, #f7fbff);

    border: 1px solid #cfe7fb;

    border-radius: 15px;

    padding: 15px 18px;

    color: #52677f;

    font-size: 12px;

    line-height: 1.6;
}

.info-title {
    color: #0d68c5;

    font-weight: 800;

    margin-bottom: 4px;
}


/* ======================================
   Dataframe
====================================== */

div[data-testid="stDataFrame"] {
    border-radius: 14px;

    overflow: hidden;

    border: 1px solid #e0e8f2;
}


/* ======================================
   Footer
====================================== */

.footer {
    text-align: center;

    color: #91a0b2;

    font-size: 11px;

    padding: 25px 0 5px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------
# Data
# --------------------------------------

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_data():

    executive = pd.read_csv(
        PROCESSED_DIR / "executive_decision.csv"
    )

    fact_sales = pd.read_parquet(
        PROCESSED_DIR / "fact_sales.parquet"
    )

    fact_forecast = pd.read_parquet(
        PROCESSED_DIR / "fact_forecast.parquet"
    )

    fact_inventory = pd.read_csv(
        PROCESSED_DIR / "fact_inventory.csv"
    )

    dim_store = pd.read_csv(
        PROCESSED_DIR / "dim_store.csv"
    )

    dim_product = pd.read_csv(
        PROCESSED_DIR / "dim_product.csv"
    )

    fact_sales["date"] = pd.to_datetime(fact_sales["date"])
    fact_forecast["date"] = pd.to_datetime(fact_forecast["date"])

    return (
        executive,
        fact_sales,
        fact_forecast,
        fact_inventory,
        dim_store,
        dim_product,
    )


# --------------------------------------
# Load Data
# --------------------------------------

try:

    (
        executive,
        fact_sales,
        fact_forecast,
        fact_inventory,
        dim_store,
        dim_product,
    ) = load_data()

except Exception as e:

    st.error("RetailIQ could not load the processed datasets.")

    st.code(str(e))

    st.stop()


# --------------------------------------
# Premium Sidebar
# --------------------------------------

with st.sidebar:

    # IMPORTANT: keep this HTML on ONE line so Streamlit's Markdown
    # parser never turns it into a code block.

    st.markdown(
        '<div class="sidebar-brand"><div class="sidebar-logo">▥</div><div class="sidebar-title">RetailIQ</div><div class="sidebar-subtitle">AI-Powered Business Intelligence</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-header">Workspace</div><div class="nav-description">Explore business intelligence</div>',
        unsafe_allow_html=True,
    )

    navigation_options = {
        "01  ▣  Executive Overview": "Executive Overview",
        "02  ◫  Store Performance": "Store Performance",
        "03  ◈  Product & Sales Intelligence": "Product & Sales Intelligence",
        "04  ◔  Demand Forecast": "Demand Forecast",
        "05  ◇  Inventory & Risk": "Inventory & Risk",
        "06  ✦  AI Business Recommendation": "AI Business Recommendation",
    }

    selected_navigation = st.radio(
        "Go to",
        list(navigation_options.keys()),
        index=0,
        label_visibility="collapsed",
    )

    selected_section = navigation_options[selected_navigation]


# --------------------------------------
# Main Header
# --------------------------------------

header, store_column = st.columns([3.5, 1])

with header:

    # IMPORTANT: keep this HTML on ONE line.

    st.markdown(
        '<div class="retailiq-header"><div class="header-row"><div class="header-logo">▥</div><div><div class="header-title">RetailIQ</div><div class="header-subtitle">AI-Powered Business Intelligence</div></div></div></div>',
        unsafe_allow_html=True,
    )


# --------------------------------------
# Store Selector
# --------------------------------------

stores = sorted(
    fact_sales["store_id"]
    .dropna()
    .unique()
)

with store_column:

    selected_store = st.selectbox("Store", stores)


# --------------------------------------
# Selected Dashboard Section
# --------------------------------------

if selected_section == "Executive Overview":

    render_executive_overview(
        executive,
        fact_sales,
        dim_store,
        dim_product,
        selected_store,
    )

elif selected_section == "Store Performance":

    render_store_performance(
        executive,
        fact_sales,
        dim_store,
        dim_product,
        selected_store,
    )

elif selected_section == "Product & Sales Intelligence":

    render_product_sales_intelligence(
        executive,
        fact_sales,
        dim_store,
        dim_product,
        selected_store,
    )

elif selected_section == "Demand Forecast":

    render_demand_forecast(
        executive,
        fact_forecast,
        selected_store,
    )

elif selected_section == "Inventory & Risk":

    render_inventory_risk(
        executive,
        fact_inventory,
        dim_product,
        selected_store,
    )

elif selected_section == "AI Business Recommendation":

    render_ai_business_recommendation(
        executive,
        fact_sales,
        fact_forecast,
        fact_inventory,
        dim_product,
        selected_store,
    )


# --------------------------------------
# Footer
# --------------------------------------

st.markdown(
    '<div class="footer">RetailIQ • From Data to Insights to Decisions</div>',
    unsafe_allow_html=True,
)