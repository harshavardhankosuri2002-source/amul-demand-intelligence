"""
AMUL KPI Engine.
Computes executive, operational, and inventory performance metrics with strict mathematical formulas.
Handles zero-demand, missing financial data, and edge conditions gracefully.
"""

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd


def compute_executive_kpis(
    df: pd.DataFrame,
    inventory_summary_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Computes primary executive KPIs:
    - Total units sold
    - Total sales revenue
    - Current inventory units and valuation
    - Number of SKUs at stockout risk
    - Number of SKUs with excess / slow-moving inventory
    - Inventory Turnover (COGS / Average Inventory) - conditional on unit_cost
    - Recorded Wastage Rate (wasted units / total units handled)
    """
    if df.empty:
        return {}
        
    total_units_sold = float(df["units_sold"].sum())
    total_revenue = float(df["revenue"].sum()) if "revenue" in df.columns else float((df["units_sold"] * df.get("selling_price", 0)).sum())
    
    # Latest snapshot for current stock
    latest_date = df["date"].max()
    earliest_date = df["date"].min()
    date_span_days = max(1, (latest_date - earliest_date).days)
    
    latest_snapshot = df[df["date"] == latest_date]
    current_inventory_units = float(latest_snapshot["stock_on_hand"].sum())
    
    # Current inventory valuation
    if "unit_cost" in latest_snapshot.columns:
        inventory_value_inr = float((latest_snapshot["stock_on_hand"] * latest_snapshot["unit_cost"]).sum())
        has_cost_data = True
    elif "selling_price" in latest_snapshot.columns:
        # Valuation at sales price (approximate, labeled)
        inventory_value_inr = float((latest_snapshot["stock_on_hand"] * latest_snapshot["selling_price"]).sum())
        has_cost_data = False
    else:
        inventory_value_inr = None
        has_cost_data = False
        
    # Stockout and Excess SKUs count from inventory summary
    if inventory_summary_df is not None and not inventory_summary_df.empty:
        stockout_skus_count = int(inventory_summary_df["is_stockout_risk"].sum())
        excess_skus_count = int(inventory_summary_df["is_excess_risk"].sum())
        total_skus = len(inventory_summary_df)
    else:
        stockout_skus_count = 0
        excess_skus_count = 0
        total_skus = df["sku_id"].nunique()
        
    # Inventory Turnover Ratio = Annualized COGS / Average Inventory Value
    # Only calculable if unit_cost is present in the data
    inventory_turnover = None
    turnover_explanation = ""
    if has_cost_data and "unit_cost" in df.columns:
        total_cogs = float((df["units_sold"] * df["unit_cost"]).sum())
        # Estimate average inventory value across all dates
        avg_inv_units = df.groupby("date")["stock_on_hand"].sum().mean()
        avg_unit_cost = df["unit_cost"].mean()
        avg_inv_val = avg_inv_units * avg_unit_cost
        
        if avg_inv_val > 0 and date_span_days > 0:
            annualized_factor = 365.0 / date_span_days
            inventory_turnover = round((total_cogs * annualized_factor) / avg_inv_val, 2)
            turnover_explanation = f"Calculated as (Annualized COGS / Avg Inventory Value) over {date_span_days} observed days."
        else:
            turnover_explanation = "Average inventory value or timeframe is zero."
    else:
        turnover_explanation = "Unavailable: 'unit_cost' field required to calculate true COGS."
        
    # Wastage Rate = Recorded Wasted Units / (Units Sold + Recorded Wasted Units + Closing Stock)
    total_wasted = float(df["units_wasted"].sum()) if "units_wasted" in df.columns else 0.0
    total_handled = total_units_sold + total_wasted + current_inventory_units
    
    if total_handled > 0:
        wastage_rate_pct = round((total_wasted / total_handled) * 100, 2)
    else:
        wastage_rate_pct = 0.0
        
    # Average Daily Run Rate
    daily_run_rate_units = round(total_units_sold / date_span_days, 1)
    
    return {
        "total_units_sold": total_units_sold,
        "total_revenue": total_revenue,
        "current_inventory_units": current_inventory_units,
        "inventory_value_inr": inventory_value_inr,
        "has_cost_data": has_cost_data,
        "stockout_skus_count": stockout_skus_count,
        "excess_skus_count": excess_skus_count,
        "total_skus": total_skus,
        "inventory_turnover": inventory_turnover,
        "turnover_explanation": turnover_explanation,
        "total_wasted_units": total_wasted,
        "wastage_rate_pct": wastage_rate_pct,
        "daily_run_rate_units": daily_run_rate_units,
        "date_span_days": date_span_days,
        "start_date": earliest_date.strftime("%Y-%m-%d"),
        "end_date": latest_date.strftime("%Y-%m-%d"),
    }
