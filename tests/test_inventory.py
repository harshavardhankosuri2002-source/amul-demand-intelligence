"""
Automated unit tests for inventory calculations, days of cover, safety stock,
and storage-type specific threshold handling.
"""

from datetime import datetime, timedelta
import pandas as pd
import pytest
from src.inventory import (
    calculate_days_of_cover,
    compute_safety_stock,
    compute_sku_inventory_status,
)
from src.kpi import compute_executive_kpis


def test_days_of_cover_zero_demand():
    doc = calculate_days_of_cover(stock_on_hand=500, avg_daily_demand=0)
    assert doc is None, "Days of cover must be None when average daily demand is zero."


def test_days_of_cover_normal():
    doc = calculate_days_of_cover(stock_on_hand=500, avg_daily_demand=50)
    assert doc == 10.0


def test_safety_stock_formula():
    # SS = Z * sqrt(LT) * std_dev
    # Z=1.65, LT=4, std=10 => 1.65 * 2 * 10 = 33.0
    ss = compute_safety_stock(demand_std=10.0, lead_time_days=4.0, service_level_z=1.65)
    assert ss == pytest.approx(33.0, 0.01)


def test_inventory_turnover_missing_cost_data():
    df = pd.DataFrame({
        "date": [datetime(2026, 6, 1)],
        "sku_id": ["AMUL-001"],
        "units_sold": [100],
        "stock_on_hand": [500],
        # No 'unit_cost' column
    })
    kpis = compute_executive_kpis(df)
    assert kpis["inventory_turnover"] is None
    assert "unit_cost" in kpis["turnover_explanation"]


def test_storage_specific_stockout_flag():
    # Create sample dataframe with Fresh milk having only 0.5 days cover
    dates = [datetime(2026, 6, 1) + timedelta(days=i) for i in range(15)]
    rows = []
    for dt in dates:
        rows.append({
            "date": dt,
            "sku_id": "AMUL-FRSH-001",
            "product_name": "Amul Taaza",
            "category": "Fresh Milk",
            "storage_type": "Fresh",
            "region": "West Zone",
            "units_sold": 100,
            "stock_on_hand": 20,  # Far below daily demand
            "unit_cost": 45.0,
            "selling_price": 54.0,
            "lead_time_days": 1,
            "expiry_date": dt + timedelta(days=2),
        })
    df = pd.DataFrame(rows)
    inv_df = compute_sku_inventory_status(df)
    
    assert len(inv_df) == 1
    assert inv_df["is_stockout_risk"].iloc[0] is True or inv_df["is_stockout_risk"].iloc[0] == 1
    assert "Stockout" in inv_df["risk_label"].iloc[0]
