"""
AMUL | AI Demand & Distribution Intelligence System
Main Streamlit Application.
An enterprise decision-support platform for multi-temperature dairy supply chain optimization.
Includes:
- Robust schema normalization and alias mapping (handling revenue_inr, stock_closing_units, etc.)
- 10 core operational & analytical modules + Academic Documentation
- Dynamic Data-Driven Insights Engine (Demand, Stockouts, Inventory, Spoilage, Promotions, Root Causes)
- Executive PDF Report Generator (ReportLab Platypus) with clickable verified citations
- Prominent synthetic data disclaimers throughout
"""

import base64
from datetime import datetime, timedelta
import io
import os
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.api_client import DistributionApiClient
from src.data_generator import SKU_CATALOG, generate_synthetic_amul_dataset
from src.data_loader import (
    KNOWN_ALIASES,
    REQUIRED_FIELDS,
    get_data_quality_report,
    validate_and_clean_data,
)
from src.diagrams import (
    DIAGRAM_A_MERMAID,
    DIAGRAM_B_MERMAID,
    DIAGRAM_C_MERMAID,
    DIAGRAM_E_MERMAID,
    DIAGRAM_F_MERMAID,
    DIAGRAM_G_MERMAID,
    build_inventory_risk_matrix_chart,
)
from src.ui_customer_modules import (
    render_customer_intelligence_ui,
    render_chatbot_ui,
    render_campaign_centre_ui,
    render_notification_centre_ui,
    render_crm_integration_ui,
)
from src.forecasting import (
    generate_future_forecast,
    train_and_evaluate_models,
)
from src.insights_engine import compute_comprehensive_insights
from src.inventory import (
    STORAGE_PROFILES,
    compute_sku_inventory_status,
)
from src.kpi import compute_executive_kpis
from src.pdf_generator import build_amul_pdf_report
from src.recommendations import generate_ai_recommendations
from src.sources import VERIFIED_SOURCES, verify_all_sources
from src.visual_theme import (
    AMUL_AMBER,
    AMUL_BLUE,
    AMUL_GREEN,
    AMUL_NAVY,
    AMUL_NAVY_LIGHT,
    AMUL_RED,
    AMUL_WHITE,
    CUSTOM_CSS,
    apply_amul_theme,
    format_inr,
    format_units,
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Amul AI Demand & Distribution Intelligence",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Enterprise Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Helper to load and display official Amul logo with preserved proportions
def render_brand_header(data_source_mode: str, refresh_time: str):
    logo_svg_path = os.path.join(os.path.dirname(__file__), "assets", "amul_logo.svg")
    logo_html = ""
    if os.path.exists(logo_svg_path):
        with open(logo_svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
            svg_b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            logo_html = f'<img src="data:image/svg+xml;base64,{svg_b64}" alt="Amul Official Logo" style="height: 38px; width: auto; object-fit: contain; margin-right: 14px;" />'
    else:
        logo_html = '<div style="font-weight: 800; font-size: 24px; color: #C4122F; letter-spacing: -0.5px; margin-right: 14px;">Amul</div>'

    status_badge = (
        '<span class="status-pill-demo">● SYNTHETIC DEMO MODE</span>'
        if data_source_mode == "Demo Data"
        else '<span class="status-pill-live">● LIVE API CONNECTED</span>'
    )

    header_html = f"""
    <div class="amul-header-banner">
        <div style="display: flex; align-items: center;">
            {logo_html}
            <div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #0B2545; line-height: 1.1;">
                    Amul AI Demand & Distribution Intelligence
                </div>
                <div style="font-size: 0.76rem; color: #64748B; margin-top: 2px;">
                    Decision-Support Analytical Platform | Multi-Temperature Dairy Cold Chain
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            {status_badge}
            <div style="font-size: 0.72rem; color: #64748B; text-align: right;">
                Last Refreshed:<br/><b>{refresh_time}</b>
            </div>
        </div>
    </div>
    <div style="background-color: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 6px; padding: 6px 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.78rem; font-weight: 700; color: #991B1B; letter-spacing: 0.03em;">
            ⚠️ SYNTHETIC DEMO DATA — NOT ACTUAL AMUL OPERATIONAL DATA
        </span>
        <span style="font-size: 0.72rem; color: #7F1D1D;">
            Academic decision-support prototype for demonstration & research evaluation.
        </span>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# Initialize Session State
if "data_source" not in st.session_state:
    st.session_state["data_source"] = "Demo Data"
if "raw_df" not in st.session_state:
    sample_csv = os.path.join(os.path.dirname(__file__), "data", "sample_amul_distribution_data.csv")
    if os.path.exists(sample_csv):
        df_init = pd.read_csv(sample_csv)
        cleaned_init, _, _ = validate_and_clean_data(df_init)
        st.session_state["raw_df"] = cleaned_init
    else:
        df_gen = generate_synthetic_amul_dataset(days=150)
        cleaned_gen, _, _ = validate_and_clean_data(df_gen)
        st.session_state["raw_df"] = cleaned_gen
if "last_refresh_timestamp" not in st.session_state:
    st.session_state["last_refresh_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if "api_telemetry" not in st.session_state:
    st.session_state["api_telemetry"] = None
if "data_warnings" not in st.session_state:
    st.session_state["data_warnings"] = []


# SIDEBAR: Configuration, Data Ingestion, Filters
with st.sidebar:
    st.markdown(
        """
        <div style="padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid #E2E8F0;">
            <div style="font-weight: 700; color: #0B2545; font-size: 1.05rem;">Control Panel</div>
            <div style="font-size: 0.75rem; color: #64748B;">System Configuration & Filters</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Navigation Menu (16 Operational, Customer & Analytical Modules)
    nav_module = st.radio(
        "Supply Chain & Customer Module",
        [
            "1. Executive Overview",
            "2. Demand Forecasting",
            "3. Inventory & Replenishment",
            "4. Regional Distribution",
            "5. Wastage & Expiry Risk",
            "6. Promotion Analysis",
            "7. AI Recommendations",
            "8. Customer-Wise Intelligence",
            "9. Amul AI Analyst (Chatbot)",
            "10. Email Campaign Centre",
            "11. Notification Centre",
            "12. CRM & REST API Schemas",
            "13. Data Quality Audit",
            "14. Insights & PDF Report",
            "15. Architecture & Methodology",
            "16. Academic & Technical Documentation",
        ],
        index=0,
    )

    st.markdown("---")

    # 2. Data Mode Switcher
    st.markdown("<b>Data Connection Mode</b>", unsafe_allow_html=True)
    mode = st.radio(
        "Source",
        ["Demo Data", "Live API", "CSV Upload"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["data_source"] = mode

    # Handling for Live API mode
    if mode == "Live API":
        with st.expander("REST API Settings", expanded=True):
            api_url = st.text_input("Endpoint URL", value="https://api.example.com/v1/amul-distribution")
            api_key = st.text_input("API Key / Bearer Token", type="password", value="demo-token-xyz")
            timeout_s = st.slider("Timeout (seconds)", min_value=3, max_value=30, value=10)
            is_mock = st.checkbox("Simulate Live API (Sandbox)", value=True, help="Simulates external ERP feed with realistic network latency.")

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button("Test Ping"):
                    client = DistributionApiClient(base_url=api_url, api_key=api_key, timeout_seconds=timeout_s, is_mock_mode=is_mock)
                    ok, msg = client.test_connection()
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
            with col_t2:
                if st.button("Fetch API"):
                    with st.spinner("Calling distributor endpoint..."):
                        client = DistributionApiClient(base_url=api_url, api_key=api_key, timeout_seconds=timeout_s, is_mock_mode=is_mock)
                        new_df, telemetry = client.fetch_distribution_data()
                        if not new_df.empty:
                            cleaned_api, missing, warnings = validate_and_clean_data(new_df)
                            st.session_state["raw_df"] = cleaned_api
                            st.session_state["api_telemetry"] = telemetry
                            st.session_state["data_warnings"] = warnings
                            st.session_state["last_refresh_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.success(f"Fetched & normalized {len(cleaned_api):,} records!")
                            st.rerun()
                        else:
                            st.error(telemetry.get("error", "Failed to fetch from API."))

    elif mode == "CSV Upload":
        with st.expander("Upload Enterprise File", expanded=True):
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            if uploaded_file is not None:
                try:
                    df_up = pd.read_csv(uploaded_file)
                    cleaned, missing, warnings = validate_and_clean_data(df_up)
                    if missing:
                        st.error(f"Missing required columns: {', '.join(missing)}")
                    else:
                        st.session_state["raw_df"] = cleaned
                        st.session_state["data_warnings"] = warnings
                        st.session_state["last_refresh_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success(f"Loaded {len(cleaned):,} records successfully!")
                        if warnings:
                            st.caption("Normalization: " + "; ".join(warnings[:3]))
                except Exception as e:
                    st.error(f"Failed to read file: {e}")

    # Manual Refresh Trigger Button
    if st.button("↻ Refresh Data", use_container_width=True, help="Manually reloads data and recomputes all analytical metrics"):
        with st.spinner("Recalculating pipeline..."):
            if mode == "Demo Data":
                new_gen = generate_synthetic_amul_dataset(days=150, seed=int(datetime.now().timestamp()) % 1000)
                cleaned_gen, _, warnings = validate_and_clean_data(new_gen)
                st.session_state["raw_df"] = cleaned_gen
                st.session_state["data_warnings"] = warnings
            st.session_state["last_refresh_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.toast("Data refreshed successfully!", icon="✅")
            st.rerun()

    st.markdown("---")

    # 3. Global Dashboard Filters
    st.markdown("<b>Global Filters</b>", unsafe_allow_html=True)
    df_raw = st.session_state["raw_df"].copy()

    min_date = df_raw["date"].min().date()
    max_date = df_raw["date"].max().date()

    date_selection = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_selection, tuple) and len(date_selection) == 2:
        start_d, end_d = date_selection
    else:
        start_d, end_d = min_date, max_date

    # Storage Temperature Filter
    available_storage = sorted(df_raw["storage_type"].dropna().unique().tolist())
    selected_storage = st.multiselect("Storage Category", options=available_storage, default=available_storage)

    # Region Filter
    available_regions = sorted(df_raw["region"].dropna().unique().tolist())
    selected_regions = st.multiselect("Geographic Region", options=available_regions, default=available_regions)

    # SKU Filter
    available_skus = sorted(df_raw["product_name"].dropna().unique().tolist())
    selected_skus = st.multiselect("SKU Drill-Down", options=available_skus, default=[])

    # Channel Filter
    if "channel" in df_raw.columns:
        available_channels = sorted(df_raw["channel"].dropna().unique().tolist())
        selected_channels = st.multiselect("Channel", options=available_channels, default=available_channels)
    else:
        selected_channels = []

    st.markdown(
        """
        <div style="font-size: 0.70rem; color: #94A3B8; margin-top: 1.5rem; text-align: center; border-top: 1px solid #F1F5F9; padding-top: 8px;">
            Academic & Decision-Support Prototype<br/>
            All figures synthetic & simulated.
        </div>
        """,
        unsafe_allow_html=True,
    )


# Apply Global Filters to working dataset
filtered_df = df_raw[
    (df_raw["date"].dt.date >= start_d)
    & (df_raw["date"].dt.date <= end_d)
    & (df_raw["storage_type"].isin(selected_storage if selected_storage else available_storage))
    & (df_raw["region"].isin(selected_regions if selected_regions else available_regions))
]

if selected_skus:
    filtered_df = filtered_df[filtered_df["product_name"].isin(selected_skus)]

if selected_channels and "channel" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["channel"].isin(selected_channels)]

# Render Header & Synthetic Warning Banner
render_brand_header(st.session_state["data_source"], st.session_state["last_refresh_timestamp"])

# Empty state warning
if filtered_df.empty:
    st.warning("⚠️ No records match the active filters. Please broaden your date range, storage category, or region selection.")
    st.stop()

# Compute shared inventory status and executive KPIs
inv_summary = compute_sku_inventory_status(filtered_df)
exec_kpis = compute_executive_kpis(filtered_df, inv_summary)


# ==========================================
# MODULE 1: EXECUTIVE OVERVIEW
# ==========================================
if "1. Executive Overview" in nav_module:
    st.markdown("### 📊 Executive Overview & Portfolio Health")
    st.caption("Strategic decision-support summary covering aggregate velocity, valuation, stockout exposure, and inventory turnover.")

    # KPI Banner Cards
    kpi_cols = st.columns(6)

    with kpi_cols[0]:
        st.markdown(
            f"""
            <div class="amul-kpi-card">
                <div class="amul-kpi-title">Total Units Sold</div>
                <div class="amul-kpi-value">{format_units(exec_kpis['total_units_sold'])}</div>
                <div class="amul-kpi-subtext">Run Rate: {exec_kpis['daily_run_rate_units']:,} / day</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_cols[1]:
        st.markdown(
            f"""
            <div class="amul-kpi-card">
                <div class="amul-kpi-title">Sales Revenue</div>
                <div class="amul-kpi-value">{format_inr(exec_kpis['total_revenue'])}</div>
                <div class="amul-kpi-subtext">Period: {exec_kpis['date_span_days']} days</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_cols[2]:
        val_sub = "At Factory Transfer Cost" if exec_kpis["has_cost_data"] else "At Retail MRP (Approx)"
        st.markdown(
            f"""
            <div class="amul-kpi-card">
                <div class="amul-kpi-title">Current Inventory</div>
                <div class="amul-kpi-value">{format_units(exec_kpis['current_inventory_units'])}</div>
                <div class="amul-kpi-subtext">{format_inr(exec_kpis['inventory_value_inr'])} ({val_sub})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_cols[3]:
        stockout_count = exec_kpis["stockout_skus_count"]
        badge_cls = "amul-badge-alert" if stockout_count > 0 else "amul-badge-success"
        st.markdown(
            f"""
            <div class="amul-kpi-card">
                <div class="amul-kpi-title">Stockout Risk SKUs</div>
                <div class="amul-kpi-value" style="color: {'#C4122F' if stockout_count > 0 else '#16A34A'};">{stockout_count}</div>
                <div class="amul-kpi-subtext"><span class="{badge_cls}">{stockout_count} of {exec_kpis['total_skus']} SKU-regions</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_cols[4]:
        excess_count = exec_kpis["excess_skus_count"]
        st.markdown(
            f"""
            <div class="amul-kpi-card">
                <div class="amul-kpi-title">Excess / Slow Cover</div>
                <div class="amul-kpi-value" style="color: {'#D97706' if excess_count > 0 else '#16A34A'};">{excess_count}</div>
                <div class="amul-kpi-subtext"><span class="amul-badge-warning">{excess_count} SKUs above threshold</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_cols[5]:
        turnover_val = f"{exec_kpis['inventory_turnover']:.1f}x" if exec_kpis["inventory_turnover"] is not None else "N/A"
        st.markdown(
            f"""
            <div class="amul-kpi-card">
                <div class="amul-kpi-title">Inventory Turnover</div>
                <div class="amul-kpi-value">{turnover_val}</div>
                <div class="amul-kpi-subtext" title="{exec_kpis['turnover_explanation']}">Annualized Ratio (COGS/Inv)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Visual Analytics Row (Safe Aggregation)
    row1_c1, row1_c2 = st.columns([7, 5])

    with row1_c1:
        # Safe aggregation dict checking available columns
        agg_dict = {"units_sold": "sum"}
        if "revenue" in filtered_df.columns:
            agg_dict["revenue"] = "sum"
        if "stock_on_hand" in filtered_df.columns:
            agg_dict["stock_on_hand"] = "sum"

        daily_agg = filtered_df.groupby("date").agg(agg_dict).reset_index()

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=daily_agg["date"],
                y=daily_agg["units_sold"],
                mode="lines",
                name="Units Sold (Daily)",
                line=dict(color=AMUL_NAVY, width=2),
            )
        )
        # 7-day moving average overlay
        daily_agg["ma7"] = daily_agg["units_sold"].rolling(7, min_periods=1).mean()
        fig_trend.add_trace(
            go.Scatter(
                x=daily_agg["date"],
                y=daily_agg["ma7"],
                mode="lines",
                name="7-Day Moving Avg",
                line=dict(color=AMUL_RED, width=2.5, dash="dot"),
            )
        )
        apply_amul_theme(fig_trend, "Portfolio Demand Velocity (Daily Units Sold)", height=340)
        st.plotly_chart(fig_trend, use_container_width=True)

    with row1_c2:
        # Category Breakdown
        rev_col = "revenue" if "revenue" in filtered_df.columns else "units_sold"
        cat_agg = filtered_df.groupby("category")[rev_col].sum().reset_index().sort_values(by=rev_col, ascending=False)
        fig_cat = px.pie(
            cat_agg,
            values=rev_col,
            names="category",
            color_discrete_sequence=[AMUL_RED, AMUL_NAVY, AMUL_NAVY_LIGHT, "#2563EB", "#0284C7", "#D97706", "#16A34A", "#9333EA"],
            hole=0.45,
        )
        apply_amul_theme(fig_cat, "Contribution by Category", height=340)
        fig_cat.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_cat, use_container_width=True)

    # Operational Health Matrix Row
    st.markdown("#### 📦 Multi-Temperature Inventory Health Summary")
    health_cols = st.columns(4)
    for idx, (storage_type, prof) in enumerate(STORAGE_PROFILES.items()):
        sub_inv = inv_summary[inv_summary["storage_type"] == storage_type]
        with health_cols[idx]:
            st.markdown(
                f"""
                <div class="amul-panel">
                    <div style="font-weight: 700; color: #0B2545; font-size: 0.95rem; border-bottom: 2px solid {'#C4122F' if storage_type=='Fresh' else '#0B2545'}; padding-bottom: 4px;">
                        {storage_type.upper()} ({prof['temp_range']})
                    </div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 6px;">
                        SKUs Active: <b>{len(sub_inv)}</b><br/>
                        Total Stock: <b>{sub_inv['current_stock'].sum():,} units</b><br/>
                        Stockout Risk: <b style="color: #C4122F;">{sub_inv['is_stockout_risk'].sum()} SKUs</b><br/>
                        Excess Risk: <b style="color: #D97706;">{sub_inv['is_excess_risk'].sum()} SKUs</b><br/>
                        Max Cover Target: <b>{prof['max_cover_days']:.0f} days</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==========================================
# MODULE 2: DEMAND FORECASTING
# ==========================================
elif "2. Demand Forecasting" in nav_module:
    st.markdown("### 📈 Time-Series Demand Forecasting Workbench")
    st.caption(
        "Supervised ML models (Gradient Boosting, Random Forest, Ridge) benchmarked against a 7-day Seasonal Naive baseline on strictly held-out chronological test sets."
    )

    f_c1, f_c2, f_c3, f_c4 = st.columns([4, 3, 3, 2])
    with f_c1:
        sku_list = sorted(filtered_df["product_name"].unique())
        chosen_sku = st.selectbox("Select Target SKU", sku_list, index=0)
    with f_c2:
        reg_list = ["All Regions Combined"] + sorted(filtered_df["region"].unique().tolist())
        chosen_region = st.selectbox("Select Region", reg_list, index=0)
    with f_c3:
        forecast_horizon = st.select_slider("Forecast Horizon (Days)", options=[7, 14, 21, 28, 30], value=14)
    with f_c4:
        ml_model_choice = st.selectbox("ML Architecture", ["GradientBoosting", "RandomForest", "Ridge"], index=0)

    sku_df = filtered_df[filtered_df["product_name"] == chosen_sku].copy()
    if chosen_region != "All Regions Combined":
        sku_df = sku_df[sku_df["region"] == chosen_region]

    daily_ts = sku_df.groupby("date").agg({
        "units_sold": "sum",
        "promotion_flag": "max" if "promotion_flag" in sku_df.columns else "count",
        "selling_price": "mean" if "selling_price" in sku_df.columns else "count",
    }).reset_index().sort_values("date")

    if len(daily_ts) < 25:
        st.warning("⚠️ Insufficient historical data points for this SKU/region combination to perform chronological train/test splitting (minimum 25 days required).")
    else:
        eval_summary, test_results, trained_model, importance = train_and_evaluate_models(
            daily_ts, test_days=forecast_horizon, model_type=ml_model_choice
        )
        future_forecast = generate_future_forecast(daily_ts, horizon_days=forecast_horizon, model_type=ml_model_choice)

        st.markdown("#### 🧪 Model Performance on Held-Out Validation Period")
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.metric(
                "Baseline WAPE (Seasonal Naive)",
                f"{eval_summary.get('baseline_wape', 'N/A')}%" if eval_summary.get('baseline_wape') is not None else "N/A",
                help="Weighted Absolute Percentage Error on held-out test data.",
            )
        with m_c2:
            st.metric(
                f"{ml_model_choice} WAPE",
                f"{eval_summary.get('ml_wape', 'N/A')}%" if eval_summary.get('ml_wape') is not None else "N/A",
                delta=f"-{eval_summary.get('wape_delta')}% pts" if (eval_summary.get('wape_delta') and eval_summary.get('wape_delta') > 0) else None,
                delta_color="normal",
                help="WAPE = sum(|actual - pred|) / sum(actual). Lower is better.",
            )
        with m_c3:
            st.metric(
                "Model MAE (Mean Abs Error)",
                f"{eval_summary.get('ml_mae', 'N/A'):,} units",
                delta=f"Baseline: {eval_summary.get('baseline_mae', 'N/A'):,}",
                delta_color="off",
            )
        with m_c4:
            st.metric(
                "Model RMSE",
                f"{eval_summary.get('ml_rmse', 'N/A'):,} units",
                delta=f"Baseline: {eval_summary.get('baseline_rmse', 'N/A'):,}",
                delta_color="off",
            )

        fig_fc = go.Figure()
        fig_fc.add_trace(
            go.Scatter(
                x=daily_ts["date"],
                y=daily_ts["units_sold"],
                mode="lines",
                name="Historical Actual Demand",
                line=dict(color=AMUL_NAVY, width=2),
            )
        )
        if not test_results.empty:
            fig_fc.add_trace(
                go.Scatter(
                    x=test_results["date"],
                    y=test_results["ml_forecast"],
                    mode="lines",
                    name="Held-Out Test Fit",
                    line=dict(color="#64748B", width=2, dash="dash"),
                )
            )
        if not future_forecast.empty:
            fig_fc.add_trace(
                go.Scatter(
                    x=pd.concat([future_forecast["date"], future_forecast["date"][::-1]]),
                    y=pd.concat([future_forecast["upper_interval_80"], future_forecast["lower_interval_80"][::-1]]),
                    fill="toself",
                    fillcolor="rgba(196, 18, 47, 0.12)",
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    showlegend=True,
                    name="80% Prediction Interval",
                )
            )
            fig_fc.add_trace(
                go.Scatter(
                    x=future_forecast["date"],
                    y=future_forecast["forecast_demand"],
                    mode="lines+markers",
                    name=f"Forecast Demand ({forecast_horizon}d)",
                    line=dict(color=AMUL_RED, width=3),
                    marker=dict(size=6, color=AMUL_RED),
                )
            )

        apply_amul_theme(
            fig_fc,
            f"Demand Forecast: {chosen_sku} ({chosen_region}) — Next {forecast_horizon} Days",
            height=400,
        )
        st.plotly_chart(fig_fc, use_container_width=True)


# ==========================================
# MODULE 3: INVENTORY AND REPLENISHMENT
# ==========================================
elif "3. Inventory & Replenishment" in nav_module:
    st.markdown("### 📦 Inventory Optimization & Replenishment Workbench")
    st.caption("Multi-temperature reorder point calculation, safety stock sizing, days of cover analytics, and automated purchase order suggestions.")

    inv_c1, inv_c2, inv_c3 = st.columns([4, 4, 4])
    with inv_c1:
        target_service_level = st.selectbox("Target Service Level (Z)", ["90%", "95%", "98%", "99%"], index=1)
    with inv_c2:
        demand_lookback = st.slider("Demand Velocity Lookback (Days)", min_value=14, max_value=60, value=30)
    with inv_c3:
        risk_filter = st.selectbox("Filter Risk Status", ["All SKUs", "Stockout Risk Only", "Excess Inventory Only", "Optimal Only"])

    inventory_view = compute_sku_inventory_status(
        filtered_df, service_level=target_service_level, lookback_days=demand_lookback
    )

    if risk_filter == "Stockout Risk Only":
        inventory_view = inventory_view[inventory_view["is_stockout_risk"]]
    elif risk_filter == "Excess Inventory Only":
        inventory_view = inventory_view[inventory_view["is_excess_risk"]]
    elif risk_filter == "Optimal Only":
        inventory_view = inventory_view[(~inventory_view["is_stockout_risk"]) & (~inventory_view["is_excess_risk"])]

    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        st.metric("Total Replenishment Recommended", f"{inventory_view['suggested_replenishment'].sum():,} units")
    with ic2:
        st.metric("SKUs Evaluated", len(inventory_view))
    with ic3:
        st.metric("Critical Stockouts", f"{inventory_view['is_stockout_risk'].sum()} lines")
    with ic4:
        st.metric("Total Inventory Valuation", format_inr(inventory_view['stock_value_inr'].sum()))

    fig_inv = px.scatter(
        inventory_view,
        x="reorder_point",
        y="current_stock",
        color="storage_type",
        size="avg_daily_demand",
        hover_data=["product_name", "region", "days_of_cover", "suggested_replenishment", "risk_label"],
        color_discrete_map={"Fresh": AMUL_RED, "Chilled": "#2563EB", "Frozen": "#0284C7", "Ambient": "#D97706"},
    )
    max_val = max(inventory_view["reorder_point"].max(), inventory_view["current_stock"].max()) * 1.05
    fig_inv.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            name="Reorder Boundary (Stock = ROP)",
            line=dict(color="#94A3B8", width=1.5, dash="dash"),
        )
    )
    apply_amul_theme(fig_inv, "Current Stock vs Calculated Reorder Point (Points below diagonal are at Stockout Risk)", height=380)
    st.plotly_chart(fig_inv, use_container_width=True)

    st.markdown("#### 📋 SKU Replenishment Plan & Days of Cover")
    display_inv = inventory_view[[
        "sku_id",
        "product_name",
        "storage_type",
        "region",
        "current_stock",
        "avg_daily_demand",
        "lead_time_days",
        "safety_stock",
        "reorder_point",
        "days_of_cover",
        "suggested_replenishment",
        "risk_label",
    ]].copy()

    st.dataframe(
        display_inv.style.format({
            "current_stock": "{:,}",
            "avg_daily_demand": "{:.1f}",
            "lead_time_days": "{:.0f}d",
            "safety_stock": "{:,}",
            "reorder_point": "{:,}",
            "days_of_cover": "{:.1f}",
            "suggested_replenishment": "{:,}",
        }),
        use_container_width=True,
        height=320,
    )


# ==========================================
# MODULE 4: REGIONAL DISTRIBUTION
# ==========================================
elif "4. Regional Distribution" in nav_module:
    st.markdown("### 🗺️ Distribution & Regional Intelligence")
    st.caption("Evaluation of demand variation, channel velocity, and regional stockout exposure across Amul operational zones.")

    r_c1, r_c2 = st.columns(2)
    with r_c1:
        reg_sales = filtered_df.groupby("region")["units_sold"].sum().reset_index().sort_values(by="units_sold", ascending=False)
        fig_reg_bar = px.bar(
            reg_sales,
            x="region",
            y="units_sold",
            text_auto=".2s",
            color="region",
            color_discrete_sequence=[AMUL_RED, AMUL_NAVY, AMUL_NAVY_LIGHT, "#2563EB"],
        )
        apply_amul_theme(fig_reg_bar, "Total Units Sold by Geographic Zone", height=340)
        st.plotly_chart(fig_reg_bar, use_container_width=True)

    with r_c2:
        reg_risk = inv_summary.groupby("region")["is_stockout_risk"].sum().reset_index()
        fig_risk_bar = px.bar(
            reg_risk,
            x="region",
            y="is_stockout_risk",
            text="is_stockout_risk",
            color_discrete_sequence=[AMUL_RED],
        )
        apply_amul_theme(fig_risk_bar, "Stockout-Risk SKU Incidents by Zone", height=340)
        st.plotly_chart(fig_risk_bar, use_container_width=True)

    # Regional Velocity Heatmap
    st.markdown("#### 🌡️ SKU Demand Velocity Heatmap by Zone (Average Daily Units)")
    pivot_df = filtered_df.pivot_table(
        index="product_name",
        columns="region",
        values="units_sold",
        aggfunc="mean",
    ).round(1).fillna(0)

    fig_heat = px.imshow(
        pivot_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[[0, "#FFFFFF"], [0.2, "#EFF6FF"], [0.6, "#93C5FD"], [1, AMUL_RED]],
    )
    apply_amul_theme(fig_heat, "Cross-Regional SKU Velocity Matrix", height=420)
    st.plotly_chart(fig_heat, use_container_width=True)


# ==========================================
# MODULE 5: WASTAGE AND EXPIRY RISK
# ==========================================
elif "5. Wastage & Expiry Risk" in nav_module:
    st.markdown("### ⏱️ Spoilage, Shelf Life & Cold Chain Wastage Analytics")
    st.caption("Tracking recorded spoilage vs estimated near-expiry risk. Distinguishes confirmed write-offs from forecast exposure.")

    w_c1, w_c2, w_c3, w_c4 = st.columns(4)
    with w_c1:
        st.metric("Recorded Wasted Units", format_units(exec_kpis["total_wasted_units"]))
    with w_c2:
        st.metric("Recorded Wastage Rate", f"{exec_kpis['wastage_rate_pct']:.2f}%", help="Recorded Wasted Units / Total Units Handled")
    with w_c3:
        near_expiry_count = 0
        if "days_to_expiry" in inv_summary.columns:
            near_expiry_count = int((inv_summary["days_to_expiry"].dropna() <= 5).sum())
        st.metric("SKU Lots Expiring in ≤5 Days", f"{near_expiry_count} lots", delta="Immediate Action", delta_color="inverse")
    with w_c4:
        cost_rate = filtered_df["unit_cost"].mean() if "unit_cost" in filtered_df.columns else 40.0
        wasted_val = exec_kpis["total_wasted_units"] * cost_rate
        st.metric("Recorded Spoilage Value", format_inr(wasted_val))

    w_row1_c1, w_row1_c2 = st.columns(2)
    with w_row1_c1:
        waste_cat = filtered_df.groupby("storage_type")["units_wasted"].sum().reset_index()
        fig_w_cat = px.bar(
            waste_cat,
            x="storage_type",
            y="units_wasted",
            text_auto=".2s",
            color="storage_type",
            color_discrete_map={"Fresh": AMUL_RED, "Chilled": "#2563EB", "Frozen": "#0284C7", "Ambient": "#D97706"},
        )
        apply_amul_theme(fig_w_cat, "Recorded Spoilage Units by Storage Temperature", height=320)
        st.plotly_chart(fig_w_cat, use_container_width=True)

    with w_row1_c2:
        daily_waste = filtered_df.groupby("date")["units_wasted"].sum().reset_index()
        fig_w_trend = px.line(
            daily_waste,
            x="date",
            y="units_wasted",
            color_discrete_sequence=[AMUL_RED],
        )
        apply_amul_theme(fig_w_trend, "Daily Recorded Spoilage Trend", height=320)
        st.plotly_chart(fig_w_trend, use_container_width=True)


# ==========================================
# MODULE 6: PROMOTION ANALYSIS
# ==========================================
elif "6. Promotion Analysis" in nav_module:
    st.markdown("### 🏷️ Marketing & Promotional Demand Response")
    st.caption("Evaluation of volume and revenue dynamics during promotional periods. Note: Distinguishes observed correlation from true causal incrementality.")

    if "promotion_flag" not in filtered_df.columns:
        st.info("Promotional flag data is not present in the current dataset.")
    else:
        p_row1_c1, p_row1_c2 = st.columns(2)
        with p_row1_c1:
            fig_box = px.box(
                filtered_df,
                x="storage_type",
                y="units_sold",
                color="promotion_flag",
                color_discrete_map={0: AMUL_NAVY, 1: AMUL_RED},
                labels={"promotion_flag": "Is Promo"},
            )
            apply_amul_theme(fig_box, "Demand Variance: Standard vs Promotional Days", height=340)
            st.plotly_chart(fig_box, use_container_width=True)

        with p_row1_c2:
            promo_cat = filtered_df[filtered_df["promotion_flag"] == 1].groupby("category")["units_sold"].sum().reset_index().sort_values(by="units_sold", ascending=False)
            fig_p_cat = px.bar(
                promo_cat,
                x="category",
                y="units_sold",
                text_auto=".2s",
                color_discrete_sequence=[AMUL_RED],
            )
            apply_amul_theme(fig_p_cat, "Promotional Units Sold by Category", height=340)
            st.plotly_chart(fig_p_cat, use_container_width=True)


# ==========================================
# MODULE 7: AI RECOMMENDATIONS
# ==========================================
elif "7. AI Recommendations" in nav_module:
    st.markdown("### 🤖 Explainable AI Recommendation Queue")
    st.caption("Automated operational alerts with transparent triggering metrics, severity levels, affected locations, and prescriptive actions.")

    recs = generate_ai_recommendations(filtered_df, inv_summary)
    if not recs:
        st.info("No actionable exceptions triggered. Current supply chain is operating within normal tolerance limits.")
    else:
        for rec in recs:
            prio_color = "#C4122F" if rec["priority"] == "High" else ("#D97706" if rec["priority"] == "Medium" else "#2563EB")
            prio_badge_cls = "amul-badge-alert" if rec["priority"] == "High" else ("amul-badge-warning" if rec["priority"] == "Medium" else "amul-badge-info")

            st.markdown(
                f"""
                <div class="amul-panel" style="border-left: 4px solid {prio_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <span class="{prio_badge_cls}">{rec['priority'].upper()} PRIORITY</span>
                            <span style="font-size: 0.82rem; font-weight: 600; color: #0B2545; margin-left: 8px;">{rec['type']}</span>
                            <span style="font-size: 0.75rem; color: #64748B; margin-left: 6px;">[{rec['rec_id']}]</span>
                        </div>
                        <div style="font-size: 0.80rem; font-weight: 600; color: #0B2545;">
                            {rec['product_name']} | <span style="color: #64748B;">{rec['location']}</span>
                        </div>
                    </div>
                    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 6px 10px; border-radius: 4px; font-size: 0.78rem; font-family: monospace; color: #0F172A; margin-bottom: 8px;">
                        <b>Trigger Data:</b> {rec['trigger_data']}
                    </div>
                    <div style="font-size: 0.84rem; color: #334155; margin-bottom: 6px;">
                        <b>Root-Cause Rationale:</b> {rec['reason']}
                    </div>
                    <div style="font-size: 0.84rem; color: #0B2545; background-color: #FEF2F2; padding: 6px 10px; border-radius: 4px; border: 1px solid #FECACA;">
                        <b>Prescribed Action:</b> {rec['suggested_action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==========================================
# MODULE 8: CUSTOMER-WISE INTELLIGENCE
# ==========================================
elif "Customer-Wise Intelligence" in nav_module or "Customer Intelligence" in nav_module:
    render_customer_intelligence_ui(filtered_df)

# ==========================================
# MODULE 9: AMUL AI ANALYST (CHATBOT)
# ==========================================
elif "Amul AI Analyst" in nav_module or "Chatbot" in nav_module:
    render_chatbot_ui(filtered_df)

# ==========================================
# MODULE 10: EMAIL CAMPAIGN CENTRE
# ==========================================
elif "Email Campaign Centre" in nav_module:
    render_campaign_centre_ui()

# ==========================================
# MODULE 11: NOTIFICATION CENTRE
# ==========================================
elif "Notification Centre" in nav_module:
    render_notification_centre_ui()

# ==========================================
# MODULE 12: CRM & REST API SCHEMAS
# ==========================================
elif "CRM & REST API" in nav_module:
    render_crm_integration_ui()

# ==========================================
# MODULE 13: DATA QUALITY AUDIT
# ==========================================
elif "Data Quality" in nav_module:
    st.markdown("### 🛡️ Data Quality, Schema Validation & Hygiene Audit")
    st.caption("Comprehensive data health diagnostics, null distribution, negative quantity checks, and alias mapping telemetry.")

    dq_report = get_data_quality_report(filtered_df)

    # Health Score & Summary Cards
    dq_c1, dq_c2, dq_c3, dq_c4 = st.columns(4)
    with dq_c1:
        st.metric("Total Records Evaluated", f"{dq_report['total_rows']:,}")
    with dq_c2:
        st.metric("Overall Hygiene Score", f"{dq_report['overall_health_score']}/100")
    with dq_c3:
        st.metric("Duplicate Rows Detected", f"{dq_report['duplicate_rows']}")
    with dq_c4:
        st.metric("Date Span", dq_report["date_range"])

    st.markdown("#### 📋 Field Schema Audit & Null Frequency")
    if not dq_report["columns_summary"].empty:
        st.dataframe(
            dq_report["columns_summary"],
            use_container_width=True,
            height=360,
        )

    st.markdown("#### 🔄 Canonical Alias Normalization Mappings")
    st.caption("The system automatically checks and resolves alternative column headers to preserve dashboard continuity.")
    alias_rows = []
    for canon, aliases in KNOWN_ALIASES.items():
        matched = [a for a in aliases if a in df_raw.columns]
        alias_rows.append({
            "Canonical Target Field": canon,
            "Recognized Aliases": ", ".join(aliases[:4]) + ("..." if len(aliases) > 4 else ""),
            "Current Dataset Match": ", ".join(matched) if matched else "None (Using Canonical)",
            "Resolution Status": "✅ Resolved" if canon in filtered_df.columns else "⚠️ Optional Field",
        })
    st.dataframe(pd.DataFrame(alias_rows), use_container_width=True, height=280)


# ==========================================
# MODULE 14: INSIGHTS & PDF REPORT
# ==========================================
elif "Insights & PDF Report" in nav_module:
    st.markdown("### 📑 Data-Driven Insights Engine & Academic PDF Report")
    st.caption("Dynamic statistical findings computed directly from current filters, coupled with an MBA faculty evaluation PDF export.")

    insights = compute_comprehensive_insights(filtered_df)

    # Prominent PDF Generation Block
    st.markdown(
        """
        <div class="amul-panel" style="background: linear-gradient(135deg, #FFFFFF 0%, #FEF2F2 100%); border-left: 5px solid #C4122F;">
            <div style="font-weight: 700; color: #0B2545; font-size: 1.15rem; margin-bottom: 4px;">
                📄 Generate & Download Professional PDF Analysis Report
            </div>
            <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                Builds a multi-page, publication-grade academic report formatted for MBA faculty evaluation using ReportLab Platypus.
                Features running headers, 'Page X of Y' footers, embedded charts, data tables, and clickable verified references.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pdf_col1, pdf_col2 = st.columns([4, 6])
    with pdf_col1:
        if st.button("Generate and Download PDF Analysis Report", use_container_width=True):
            with st.spinner("Compiling Matplotlib figures, ReportLab tables, and verified citations..."):
                filter_str = f"Range: {start_d} to {end_d} | Categories: {', '.join(selected_storage)} | Regions: {', '.join(selected_regions)}"
                pdf_filename = "Amul_AI_Demand_Intelligence_Report.pdf"
                pdf_path = build_amul_pdf_report(filtered_df, output_filename=pdf_filename, filters_summary=filter_str)

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.session_state["generated_pdf_bytes"] = pdf_bytes
                st.session_state["generated_pdf_size"] = len(pdf_bytes)
                st.success(f"Report compiled successfully ({len(pdf_bytes):,} bytes)!")

    with pdf_col2:
        if "generated_pdf_bytes" in st.session_state:
            st.download_button(
                label=f"⬇️ Download PDF Document ({st.session_state['generated_pdf_size'] // 1024} KB)",
                data=st.session_state["generated_pdf_bytes"],
                file_name="Amul_AI_Demand_Intelligence_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    st.markdown("---")
    st.markdown("#### 🔍 Dynamic Data-Driven Analytical Insights")

    insight_tabs = st.tabs([
        "A. Demand Analysis",
        "B. Stockouts & Lost Sales",
        "C. Inventory Optimization",
        "D. Wastage & Cold Chain",
        "E. Promotion Response",
        "G. Root-Cause Analysis",
    ])

    d_info = insights.get("demand", {})
    so_info = insights.get("stockout", {})
    inv_info = insights.get("inventory", {})
    w_info = insights.get("wastage", {})
    p_info = insights.get("promotion", {})

    with insight_tabs[0]:
        st.markdown("##### A. Portfolio Demand & Seasonality Dynamics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Highest-Velocity SKU", d_info.get("top_sku", "N/A"), f"{d_info.get('top_sku_vol', 0):,} units")
        c2.metric("Dominant Category", d_info.get("top_category", "N/A"), f"{d_info.get('top_cat_share_pct', 0)}% volume share")
        c3.metric("Weekend Demand Lift", f"+{d_info.get('weekend_lift_pct', 0)}%", "vs Weekday run-rate")
        st.markdown(f"• **Temperature Elasticity:** Cold beverage/ice-cream correlation with temperature is **r = {d_info.get('temperature_cold_corr', 0)}**.")
        st.markdown(f"• **Festival Lift:** Festival period observations generated an observed volume lift of **+{d_info.get('festival_lift_pct', 0)}%**.")

    with insight_tabs[1]:
        st.markdown("##### B. Stockout Exposure & Unserved Demand")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Stockouts", f"{so_info.get('stockout_count', 0):,} incidents", f"{so_info.get('stockout_rate_pct', 0)}% incident rate")
        c2.metric("Estimated Lost Demand", format_units(so_info.get('total_lost_sales_units', 0)))
        c3.metric("Delay Stockout Odds", f"{so_info.get('delay_stockout_odds_ratio', 1.0):.1f}x", "Higher under delivery delay")
        st.markdown(f"• **Highest Stockout SKU:** **{so_info.get('top_stockout_sku', 'N/A')}** experienced {so_info.get('top_stockout_count', 0)} recorded stockout events.")

    with insight_tabs[2]:
        st.markdown("##### C. Inventory Cover & Working Capital")
        c1, c2, c3 = st.columns(3)
        c1.metric("Closing Stock Volume", format_units(inv_info.get("closing_stock_units", 0)))
        c2.metric("Median Days of Cover", f"{inv_info.get('median_days_of_cover', 0)} days")
        c3.metric("Critical Cover (<3d)", f"{inv_info.get('skus_low_cover_count', 0)} SKUs")

    with insight_tabs[3]:
        st.markdown("##### D. Wastage, Shelf Life & Cold Chain Breaches")
        c1, c2, c3 = st.columns(3)
        c1.metric("Recorded Spoilage", format_units(w_info.get("total_wasted_units", 0)))
        c2.metric("Recorded Wastage Rate", f"{w_info.get('wastage_rate_pct', 0)}%", "Wasted / Units Handled")
        c3.metric("Fresh Category Share", f"{w_info.get('fresh_spoilage_share_pct', 0)}%", "of total spoilage")
        st.markdown(f"• **Cold-Chain Excursions:** Temperature breaches (>4°C) associate with a **{w_info.get('excursion_waste_multiplier', 1.0)}x** increase in spoilage units.")

    with insight_tabs[4]:
        st.markdown("##### E. Promotion Response & Elasticity")
        c1, c2 = st.columns(2)
        c1.metric("Observed Promotional Lift", f"+{p_info.get('promo_lift_pct', 0)}%", f"Promo: {p_info.get('promo_avg_units', 0)} vs Non-Promo: {p_info.get('non_promo_avg_units', 0)}")
        c2.metric("Promo Revenue Contribution", f"{p_info.get('promo_revenue_share_pct', 0)}%")
        st.caption("Note: Observed uplifts reflect empirical correlations. Incremental uplift requires controlled test-versus-control market trials.")

    with insight_tabs[5]:
        st.markdown("##### G. Ranked Root-Cause Operational Drivers")
        rc_list = insights.get("root_causes", [])
        if rc_list:
            rc_df = pd.DataFrame(rc_list)
            st.dataframe(
                rc_df[["risk_type", "driver_factor", "correlation_score", "odds_ratio", "interpretation"]].rename(columns={
                    "risk_type": "Supply Chain Risk",
                    "driver_factor": "Associated Operational Factor",
                    "correlation_score": "Correlation (r)",
                    "odds_ratio": "Impact Ratio",
                    "interpretation": "Empirical Interpretation & Prescribed Action",
                }),
                use_container_width=True,
            )


# ==========================================
# MODULE 15: ARCHITECTURE & METHODOLOGY
# ==========================================
elif "Architecture & Methodology" in nav_module:
    st.markdown("### 🏛️ System Architecture & Conceptual Diagrams")
    st.caption("Comprehensive supply-chain and algorithmic methodology diagrams for the Amul AI Demand Intelligence platform.")

    diag_tabs = st.tabs([
        "Diagram A: Value Chain",
        "Diagram B: Architecture",
        "Diagram C: Forecasting Workflow",
        "Diagram D: Risk Matrix",
        "Diagram E: Ishikawa Fishbone",
        "Diagram F: Feedback Loop",
        "Diagram G: Customer Campaign Workflow",
    ])

    with diag_tabs[0]:
        st.markdown("#### Diagram A: Dairy Supply Chain Business Value Chain")
        st.caption("End-to-end physical product movement from village milk societies to consumers, overlaid with upstream demand/inventory telemetry signals.")
        st.markdown(f"```mermaid\n{DIAGRAM_A_MERMAID}\n```")

    with diag_tabs[1]:
        st.markdown("#### Diagram B: System Architecture & Ingestion Pipeline")
        st.caption("Data ingestion, validation gate, feature engineering, multi-temperature business logic, and Streamlit presentation layer.")
        st.markdown(f"```mermaid\n{DIAGRAM_B_MERMAID}\n```")

    with diag_tabs[2]:
        st.markdown("#### Diagram C: Demand Forecasting Workflow")
        st.caption("Chronological time-series splitting, feature matrix creation, baseline benchmarking, and validation gates.")
        st.markdown(f"```mermaid\n{DIAGRAM_C_MERMAID}\n```")

    with diag_tabs[3]:
        st.markdown("#### Diagram D: Multi-Temperature Inventory Risk Matrix")
        st.caption("Interactive 2x2 scatter matrix categorizing active SKU lots into Critical Stockout, Volatile, Optimal, and Excess/Spoilage quadrants.")
        fig_quad = build_inventory_risk_matrix_chart(inv_summary)
        st.plotly_chart(fig_quad, use_container_width=True)

    with diag_tabs[4]:
        st.markdown("#### Diagram E: Ishikawa (Fishbone) Supply-Demand Root Cause Hypotheses")
        st.caption("Hypotheses for supply chain variance across Demand, Inventory, Distribution, Product, and Data Visibility.")
        st.markdown(f"```mermaid\n{DIAGRAM_E_MERMAID}\n```")

    with diag_tabs[5]:
        st.markdown("#### Diagram F: Closed-Loop Model Retraining Feedback Loop")
        st.caption("Continuous cycle connecting model forecasts, real-world replenishment actions, observed errors, and automated model recalibration.")
        st.markdown(f"```mermaid\n{DIAGRAM_F_MERMAID}\n```")

    with diag_tabs[6]:
        st.markdown("#### Diagram G: End-to-End Customer Campaign & Notification Workflow")
        st.caption("Closed-loop customer campaign workflow integrating DPDPA consent verification, RFM segmentation, internal test sends, and human approval gates.")
        st.markdown(f"```mermaid\n{DIAGRAM_G_MERMAID}\n```")


# ==========================================
# MODULE 16: ACADEMIC & TECHNICAL DOCUMENTATION
# ==========================================
elif "Academic & Technical Documentation" in nav_module:
    st.markdown("### 📚 Academic Presentation & Technical Reference")
    st.caption("Formal documentation of business context, mathematical formulations, assumptions, and verified sources.")

    doc_tabs = st.tabs([
        "1. Business Context & Problem",
        "2. Solution Architecture",
        "3. Mathematical Formulas",
        "4. Operational Initiatives at Amul",
        "5. Verified Source Registry",
    ])

    with doc_tabs[0]:
        st.markdown(
            """
            #### 1. Business Context & Problem Statement
            **Amul (Gujarat Cooperative Milk Marketing Federation - GCMMF)** is the world's largest farmer-owned dairy cooperative. 
            Unlike single-temperature FMCG manufacturers, Amul manages a uniquely diversified multi-echelon portfolio:
            - **Fresh Dairy (2-4°C)**: Ultra-perishable (2-3 day shelf life for pouch milk), requiring daily distribution cycles.
            - **Chilled Dairy (0-4°C)**: Butter and cheese blocks requiring cold room storage and regional depot buffers.
            - **Frozen Dairy (-18°C)**: Ice creams and frozen vegetables requiring deep cold chain integrity.
            - **Ambient Products**: Ghee, sweetened condensed milk, UHT drinks, and chocolates with extended shelf lives.

            **Core Operational Challenge:**
            Balancing product availability across 1 million+ retail touchpoints while minimizing avoidable milk return spoilage, stockouts during seasonal peaks, and working capital blockage.
            """
        )

    with doc_tabs[1]:
        st.markdown(
            """
            #### 2. Proposed Solution & Decision-Support Scope
            This system functions as a **decision-support layer** designed to complement Amul's existing SAP/ERP and Distributor Management Systems (DMS):
            - **Automated Anomaly Detection**: Highlights SKU-region pairs experiencing unseasonal demand spikes or stockout threats.
            - **Cold-Chain Differentiated Policies**: Dynamic safety stocks adjusted for product shelf life rather than blanket inventory rules.
            - **Explainable Prescriptive Actions**: Plain-language recommendations detailing triggering data, priority, and concrete actions.
            """
        )

    with doc_tabs[2]:
        st.markdown(
            """
            #### 3. Strict Mathematical Formulations

            ##### A. Weighted Absolute Percentage Error (WAPE)
            $$\\text{WAPE} = \\frac{\\sum_{t=1}^{n} |A_t - F_t|}{\\sum_{t=1}^{n} A_t} \\times 100$$
            *Zero Demand Handling:* If $\\sum A_t = 0$, WAPE is mathematically undefined; displayed as `N/A` rather than throwing a division-by-zero exception.

            ##### B. Statistical Safety Stock
            $$\\text{Safety Stock} = Z \\times \\sqrt{L \\cdot \\sigma_D^2 + D^2 \\cdot \\sigma_L^2}$$
            Where $Z$ is the standard normal score for the target service level (e.g., $1.65$ for $95\\%$), $L$ is lead time, and $D$ is average daily demand.

            ##### C. Reorder Point (ROP)
            $$\\text{ROP} = (\\text{Average Daily Demand} \\times \\text{Lead Time}) + \\text{Safety Stock}$$

            ##### D. Days of Cover (DOC)
            $$\\text{Days of Cover} = \\frac{\\text{Available Usable Stock}}{\\text{Average Daily Demand}}$$
            *Edge Handling:* If demand is zero, returns `None` (labeled as infinite cover).
            """
        )

    with doc_tabs[3]:
        st.markdown(
            """
            #### 4. Reported Operational Initiatives by GCMMF (Amul)
            Amul has publicly described several industry-leading operational modernization programs:
            - **SKU-Range Rationalization**: Optimizing regional pack sizes to maximize delivery vehicle fill rates.
            - **Hub-and-Spoke Depots**: Modern mother dairies feeding regional CF&A (Carrying & Forwarding) centers.
            - **Weekly S&OP Planning**: Synchronizing milk union procurement with metropolitan retail demand.
            - **Cold Chain Temperature Telematics**: Continuous GPS and temperature sensor tracking on reefer vehicles.
            """
        )

    with doc_tabs[4]:
        st.markdown("#### 5. Verified External Citations & Factual Sources")
        st.caption("All factual and institutional claims are grounded in verified external references:")

        sources_list = verify_all_sources(timeout_seconds=3)
        st.dataframe(
            pd.DataFrame(sources_list)[["title", "organization", "url", "verification_status", "verified_date"]].rename(columns={
                "title": "Document Title",
                "organization": "Publishing Body",
                "url": "Verified URL",
                "verification_status": "Verification Status",
                "verified_date": "Verified Date",
            }),
            use_container_width=True,
        )
