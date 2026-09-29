"""
AMUL AI Recommendations Engine.
Generates evidence-based, explainable prescriptive recommendations for supply chain operators.
Every recommendation contains:
- ID & Timestamp
- Category (Replenishment, Expiry Alert, Slow Mover, Demand Surge, Forecast Bias)
- Affected SKU / Location / Channel
- Priority (High, Medium, Low)
- Triggering Data (Quantified metrics)
- Reason (Explainable operational rationale)
- Suggested Action (Concrete next steps)
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd


def generate_ai_recommendations(
    df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    max_recommendations: int = 15,
) -> List[Dict[str, Any]]:
    """
    Evaluates current inventory status, sales trends, expiry risks,
    and regional variations to produce explainable supply chain action items.
    """
    recommendations = []
    
    if inventory_df.empty or df.empty:
        return recommendations

    # 1. Critical Replenishment Recommendations (Stockout Risk)
    critical_stockouts = inventory_df[inventory_df["is_stockout_risk"]].sort_values(
        by=["storage_type", "days_of_cover"], ascending=[True, True]
    )
    
    for _, row in critical_stockouts.head(5).iterrows():
        sku = row["sku_id"]
        p_name = row["product_name"]
        region = row["region"]
        doc = row["days_of_cover"] if row["days_of_cover"] is not None else 0.0
        lt = row["lead_time_days"]
        current_stock = row["current_stock"]
        rop = row["reorder_point"]
        suggested_qty = row["suggested_replenishment"]
        storage = row["storage_type"]
        
        is_urgent = doc < lt
        priority = "High" if is_urgent or storage == "Fresh" else "Medium"
        
        recommendations.append({
            "rec_id": f"REC-REP-{sku[:9]}-{np.random.randint(100, 999)}",
            "type": "Replenishment Trigger",
            "priority": priority,
            "sku_id": sku,
            "product_name": p_name,
            "location": region,
            "trigger_data": f"Current Stock: {current_stock:,} units | Reorder Point: {rop:,} units | Days of Cover: {doc:.1f}d (Lead Time: {lt:.0f}d)",
            "reason": (
                f"Available inventory in {region} has fallen below the calculated Reorder Point ({rop:,} units). "
                f"With only {doc:.1f} days of cover remaining against a replenishment lead time of {lt:.0f} days, "
                f"there is an immediate stockout risk for this {storage} product line."
            ),
            "suggested_action": f"Dispatch expedited replenishment order of {suggested_qty:,} units from primary regional mother dairy / CF&A depot.",
        })
        
    # 2. Expiry & Spoilage Prevention (Fresh & Chilled SKUs nearing shelf life)
    if "days_to_expiry" in inventory_df.columns:
        expiring_soon = inventory_df[
            (inventory_df["days_to_expiry"].notna())
            & (inventory_df["days_to_expiry"] <= 5)
            & (inventory_df["current_stock"] > 0)
        ].sort_values(by="days_to_expiry", ascending=True)
        
        for _, row in expiring_soon.head(4).iterrows():
            sku = row["sku_id"]
            p_name = row["product_name"]
            region = row["region"]
            days_left = int(row["days_to_expiry"])
            stock = row["current_stock"]
            daily_sales = row["avg_daily_demand"]
            expected_sales_before_expiry = daily_sales * max(1, days_left)
            at_risk_qty = max(0, int(stock - expected_sales_before_expiry))
            
            if at_risk_qty > 0 or days_left <= 2:
                recommendations.append({
                    "rec_id": f"REC-EXP-{sku[:9]}-{np.random.randint(100, 999)}",
                    "type": "Expiry Risk Mitigation",
                    "priority": "High" if days_left <= 2 else "Medium",
                    "sku_id": sku,
                    "product_name": p_name,
                    "location": region,
                    "trigger_data": f"Shelf Life Remaining: {days_left} days | On-Hand Stock: {stock:,} units | Daily Demand: {daily_sales:.0f} units/day",
                    "reason": (
                        f"Current stock of {stock:,} units exceeds projected absorption ({expected_sales_before_expiry:.0f} units) "
                        f"prior to batch expiry date. Estimated {at_risk_qty:,} units face direct spoilage if not moved."
                    ),
                    "suggested_action": (
                        "Trigger immediate FIFO prioritisation, transfer stock to high-velocity modern trade / quick commerce channels, "
                        "or initiate tactical retail promotional discount."
                    ),
                })

    # 3. Slow-Moving / Overstock Review
    excess_skus = inventory_df[inventory_df["is_excess_risk"]].sort_values(
        by="days_of_cover", ascending=False
    )
    for _, row in excess_skus.head(3).iterrows():
        sku = row["sku_id"]
        p_name = row["product_name"]
        region = row["region"]
        doc = row["days_of_cover"] if row["days_of_cover"] is not None else 99.0
        val = row["stock_value_inr"]
        storage = row["storage_type"]
        
        recommendations.append({
            "rec_id": f"REC-EXC-{sku[:9]}-{np.random.randint(100, 999)}",
            "type": "Excess Inventory Review",
            "priority": "Low" if storage == "Ambient" else "Medium",
            "sku_id": sku,
            "product_name": p_name,
            "location": region,
            "trigger_data": f"Days of Cover: {doc:.1f} days | Inventory Valuation: ₹{val:,.0f} | Category: {storage}",
            "reason": (
                f"Stock cover ({doc:.1f} days) substantially exceeds upper threshold for {storage} storage. "
                f"Blocks working capital (₹{val:,.0f}) and incurs avoidable cold storage or warehouse footprint costs."
            ),
            "suggested_action": (
                "Temporarily halt automated purchase orders for this SKU, bundle with high-velocity festive packs, "
                "or redistribute to neighboring distribution nodes experiencing stock pressure."
            ),
        })

    # 4. Regional Demand Surge Alert
    # Check last 7 days vs previous 21 days for demand spikes
    recent_date = df["date"].max()
    t_minus_7 = recent_date - pd.Timedelta(days=7)
    t_minus_28 = recent_date - pd.Timedelta(days=28)
    
    last_7_sales = df[df["date"] >= t_minus_7].groupby(["sku_id", "region"])["units_sold"].mean()
    prior_sales = df[(df["date"] >= t_minus_28) & (df["date"] < t_minus_7)].groupby(["sku_id", "region"])["units_sold"].mean()
    
    merged_growth = pd.DataFrame({"last_7": last_7_sales, "prior": prior_sales}).dropna()
    merged_growth["surge_pct"] = ((merged_growth["last_7"] - merged_growth["prior"]) / merged_growth["prior"].replace(0, np.nan)) * 100
    
    surges = merged_growth[merged_growth["surge_pct"] > 35].sort_values(by="surge_pct", ascending=False)
    for (sku, reg), s_row in surges.head(3).iterrows():
        p_name = df[df["sku_id"] == sku]["product_name"].iloc[0]
        surge_val = s_row["surge_pct"]
        recent_avg = s_row["last_7"]
        prior_avg = s_row["prior"]
        
        recommendations.append({
            "rec_id": f"REC-SRG-{sku[:9]}-{np.random.randint(100, 999)}",
            "type": "Demand Spike Investigation",
            "priority": "Medium",
            "sku_id": sku,
            "product_name": p_name,
            "location": reg,
            "trigger_data": f"7-Day Demand Spike: +{surge_val:.1f}% ({recent_avg:.0f} vs {prior_avg:.0f} units/day baseline)",
            "reason": (
                f"Abrupt 7-day velocity increase detected in {reg}. Could indicate unlogged localized promotion, "
                f"weather-driven impulse buying, or rival brand availability failure."
            ),
            "suggested_action": (
                "Review distributor stock levels in the zone; verify whether additional safety stock should be assigned "
                "to prevent stockouts over the coming two weekly cycles."
            ),
        })

    return recommendations[:max_recommendations]
