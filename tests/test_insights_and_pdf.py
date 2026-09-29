"""
Automated unit tests for data normalization, alias resolution,
insights engine calculations, and PDF report generation.
"""

from datetime import datetime, timedelta
import os
import numpy as np
import pandas as pd
import pytest
from src.data_loader import get_data_quality_report, validate_and_clean_data
from src.insights_engine import compute_comprehensive_insights
from src.pdf_generator import build_amul_pdf_report


def test_schema_mapping_revenue_inr_and_stock_closing():
    """
    Validates Part 1 requirement:
    - revenue = revenue_inr if revenue missing
    - stock_on_hand = stock_closing_units if stock_on_hand missing
    - Never overwrite existing valid canonical column
    """
    raw_df = pd.DataFrame({
        "date": ["2026-06-01", "2026-06-02"],
        "sku_id": ["AMUL-001", "AMUL-001"],
        "product_name": ["Amul Taaza", "Amul Taaza"],
        "category": ["Fresh Milk", "Fresh Milk"],
        "units_sold": [100, 150],
        "revenue_inr": [5400.0, 8100.0],
        "stock_closing_units": [450, 300],
        "units_demanded_est": [100, 160],
        "lost_sales_estimate": [0, 10],
    })

    cleaned, missing, warnings = validate_and_clean_data(raw_df)

    assert len(missing) == 0, f"Expected 0 missing columns, got: {missing}"
    assert "revenue" in cleaned.columns
    assert "stock_on_hand" in cleaned.columns
    assert cleaned["revenue"].iloc[0] == 5400.0
    assert cleaned["stock_on_hand"].iloc[0] == 450
    # Original aliases must also be preserved
    assert "revenue_inr" in cleaned.columns
    assert "stock_closing_units" in cleaned.columns


def test_no_overwrite_existing_canonical_column():
    """Validates that existing valid canonical column is not overwritten with empty alias."""
    raw_df = pd.DataFrame({
        "date": ["2026-06-01"],
        "sku_id": ["AMUL-001"],
        "product_name": ["Amul Taaza"],
        "category": ["Fresh Milk"],
        "units_sold": [100],
        "revenue": [5400.0],
        "revenue_inr": [np.nan],  # Empty alias
        "stock_on_hand": [500],
        "stock_closing_units": [None],  # Empty alias
    })

    cleaned, missing, warnings = validate_and_clean_data(raw_df)
    assert cleaned["revenue"].iloc[0] == 5400.0
    assert cleaned["stock_on_hand"].iloc[0] == 500


def test_safe_daily_aggregation_does_not_throw_keyerror():
    """Validates that grouping by date and aggregating revenue and stock does not crash."""
    raw_df = pd.DataFrame({
        "date": ["2026-06-01", "2026-06-02"],
        "sku_id": ["AMUL-001", "AMUL-002"],
        "product_name": ["Amul Taaza", "Amul Gold"],
        "category": ["Fresh Milk", "Fresh Milk"],
        "units_sold": [100, 200],
        "revenue_inr": [5400.0, 6600.0],
        "stock_closing_units": [400, 500],
    })

    cleaned, missing, warnings = validate_and_clean_data(raw_df)
    # Perform aggregation identical to app.py
    agg_dict = {
        "units_sold": "sum",
        "revenue": "sum",
        "stock_on_hand": "sum",
    }
    grouped = cleaned.groupby("date").agg(agg_dict).reset_index()
    assert len(grouped) == 2
    assert "revenue" in grouped.columns
    assert grouped["revenue"].sum() == 12000.0


def test_data_quality_report():
    raw_df = pd.DataFrame({
        "date": ["2026-06-01", "2026-06-02"],
        "sku_id": ["AMUL-001", "AMUL-001"],
        "product_name": ["Amul Taaza", "Amul Taaza"],
        "category": ["Fresh Milk", "Fresh Milk"],
        "units_sold": [100, 150],
        "stock_on_hand": [500, 450],
        "revenue": [5400.0, 8100.0],
    })
    cleaned, _, _ = validate_and_clean_data(raw_df)
    dq = get_data_quality_report(cleaned)
    assert dq["total_rows"] == 2
    assert dq["sku_count"] == 1
    assert dq["overall_health_score"] >= 90


def test_insights_engine_computation():
    dates = [datetime(2026, 6, 1) + timedelta(days=i) for i in range(20)]
    df = pd.DataFrame({
        "date": dates,
        "sku_id": ["AMUL-FRSH-001"] * 20,
        "product_name": ["Amul Taaza 1L"] * 20,
        "category": ["Fresh Milk"] * 20,
        "storage_type": ["Fresh"] * 20,
        "region": ["West Zone"] * 20,
        "units_sold": [100 + i for i in range(20)],
        "units_demanded_est": [105 + i for i in range(20)],
        "lost_sales_estimate": [5] * 20,
        "stock_on_hand": [200] * 20,
        "stock_closing_units": [200] * 20,
        "revenue": [5400.0] * 20,
        "revenue_inr": [5400.0] * 20,
        "stockout_flag": [1 if i % 5 == 0 else 0 for i in range(20)],
        "delivery_delay_flag": [1 if i % 4 == 0 else 0 for i in range(20)],
        "cold_chain_excursion_flag": [0] * 20,
        "festival_flag": [1 if i in [10, 11] else 0 for i in range(20)],
        "units_wasted": [2] * 20,
        "lead_time_days": [2] * 20,
        "selling_price": [54.0] * 20,
        "unit_cost": [46.0] * 20,
        "promotion_flag": [1 if i % 6 == 0 else 0 for i in range(20)],
    })

    insights = compute_comprehensive_insights(df)
    assert "demand" in insights
    assert "stockout" in insights
    assert "inventory" in insights
    assert "wastage" in insights
    assert "promotion" in insights
    assert "root_causes" in insights
    assert insights["demand"]["total_units_sold"] > 0
    assert insights["stockout"]["stockout_count"] == 4


def test_pdf_generation():
    dates = [datetime(2026, 6, 1) + timedelta(days=i) for i in range(30)]
    df = pd.DataFrame({
        "date": dates,
        "sku_id": ["AMUL-001"] * 30,
        "product_name": ["Amul Taaza 1L"] * 30,
        "category": ["Fresh Milk"] * 30,
        "storage_type": ["Fresh"] * 30,
        "region": ["West Zone"] * 30,
        "units_sold": [100 + (i % 7) * 10 for i in range(30)],
        "units_demanded_est": [110 + (i % 7) * 10 for i in range(30)],
        "lost_sales_estimate": [10] * 30,
        "stock_on_hand": [300] * 30,
        "stock_closing_units": [300] * 30,
        "revenue": [5400.0] * 30,
        "revenue_inr": [5400.0] * 30,
        "stockout_flag": [1 if i % 6 == 0 else 0 for i in range(30)],
        "delivery_delay_flag": [1 if i % 5 == 0 else 0 for i in range(30)],
        "cold_chain_excursion_flag": [0] * 30,
        "festival_flag": [0] * 30,
        "units_wasted": [1] * 30,
        "lead_time_days": [2] * 30,
        "selling_price": [54.0] * 30,
        "unit_cost": [46.0] * 30,
        "promotion_flag": [0] * 30,
    })

    out_pdf = "test_unit_report.pdf"
    res_path = build_amul_pdf_report(df, out_pdf)
    assert os.path.exists(res_path)
    with open(res_path, "rb") as f:
        pdf_bytes = f.read()
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 20000  # Multi-page PDF with charts and tables

    # Clean up test output
    if os.path.exists(out_pdf):
        os.remove(out_pdf)
