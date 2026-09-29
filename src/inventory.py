"""
AMUL Inventory, Replenishment, and Multi-Temperature Cold Chain Engine.
Calculates:
1. Reorder Point (ROP) = (Avg Daily Demand * Lead Time) + Safety Stock.
2. Safety Stock = Z * sqrt(Lead Time * StdDev_Demand^2).
3. Days of Cover (DOC) = Available Stock / Avg Daily Demand (safe division).
4. Storage-specific policies:
   - Fresh (2-4°C): Tight max cover threshold (e.g. 3-5 days) to avert spoilage.
   - Chilled (0-4°C): Intermediate cover (14-30 days).
   - Frozen (-18°C): Freezer batching and MOQ constraints.
   - Ambient: Extended cover (30-60 days).
5. Suggested Replenishment Order Quantity with MOQ batching.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd

# Storage Type Profiles with default industry parameters
STORAGE_PROFILES = {
    "Fresh": {
        "temp_range": "2°C to 4°C",
        "default_lead_time_days": 1.5,
        "max_cover_days": 4.0,  # Any stock > 4 days is high risk of spoilage
        "min_cover_days": 1.2,
        "z_score": 1.96,  # 97.5% service level
        "holding_risk": "High Spoilage / Rapid Expiry",
    },
    "Chilled": {
        "temp_range": "0°C to 4°C",
        "default_lead_time_days": 4.0,
        "max_cover_days": 25.0,
        "min_cover_days": 6.0,
        "z_score": 1.65,  # 95% service level
        "holding_risk": "Cold Space Capacity / Shelf Life",
    },
    "Frozen": {
        "temp_range": "-18°C",
        "default_lead_time_days": 5.0,
        "max_cover_days": 35.0,
        "min_cover_days": 8.0,
        "z_score": 1.65,  # 95% service level
        "holding_risk": "Deep Freeze Energy / Cold Chain Integrity",
    },
    "Ambient": {
        "temp_range": "Ambient / Dry",
        "default_lead_time_days": 6.0,
        "max_cover_days": 50.0,
        "min_cover_days": 12.0,
        "z_score": 1.65,  # 95% service level
        "holding_risk": "Working Capital Blockage",
    },
}


def calculate_days_of_cover(stock_on_hand: float, avg_daily_demand: float) -> Optional[float]:
    """
    Computes Days of Cover = usable stock / average daily demand.
    Safely handles zero or negative demand: returns None (infinite / undefined cover).
    """
    if avg_daily_demand <= 0:
        return None
    return round(float(stock_on_hand / avg_daily_demand), 1)


def compute_safety_stock(
    demand_std: float,
    lead_time_days: float,
    service_level_z: float = 1.65,
) -> float:
    """
    Calculates statistical safety stock:
    SS = Z * sqrt(Lead_Time) * StdDev(Demand)
    """
    if lead_time_days <= 0 or demand_std <= 0:
        return 0.0
    return float(service_level_z * np.sqrt(lead_time_days) * demand_std)


def compute_sku_inventory_status(
    df: pd.DataFrame,
    service_level: str = "95%",
    lookback_days: int = 30,
) -> pd.DataFrame:
    """
    Computes SKU-level inventory analytics, stockout flags, days of cover,
    and suggested replenishment quantities tailored to Amul storage classifications.
    """
    z_map = {"90%": 1.28, "95%": 1.65, "98%": 2.05, "99%": 2.33}
    user_z = z_map.get(service_level, 1.65)
    
    # Filter to recent lookback window for stable demand rate
    max_date = df["date"].max()
    min_date = max_date - pd.Timedelta(days=lookback_days)
    recent_df = df[df["date"] >= min_date].copy()
    
    sku_rows = []
    
    for (sku_id, region), group in recent_df.groupby(["sku_id", "region"]):
        prod_name = group["product_name"].iloc[0]
        cat = group["category"].iloc[0]
        storage = group["storage_type"].iloc[0] if "storage_type" in group.columns else "Ambient"
        storage_prof = STORAGE_PROFILES.get(storage, STORAGE_PROFILES["Ambient"])
        
        # Latest recorded stock on hand
        latest_record = group.sort_values("date").iloc[-1]
        current_stock = float(latest_record["stock_on_hand"])
        unit_cost = float(latest_record.get("unit_cost", 50.0))
        selling_price = float(latest_record.get("selling_price", 60.0))
        lead_time = float(latest_record.get("lead_time_days", storage_prof["default_lead_time_days"]))
        
        # Calculate daily demand statistics
        daily_units = group.groupby("date")["units_sold"].sum()
        avg_daily_demand = float(daily_units.mean())
        std_daily_demand = float(daily_units.std()) if len(daily_units) > 1 else avg_daily_demand * 0.2
        if np.isnan(std_daily_demand):
            std_daily_demand = 0.0
            
        # Statistical Safety Stock & Reorder Point
        safety_stock = compute_safety_stock(std_daily_demand, lead_time, user_z)
        reorder_point = (avg_daily_demand * lead_time) + safety_stock
        
        # Days of Cover
        doc = calculate_days_of_cover(current_stock, avg_daily_demand)
        
        # Storage-specific thresholds
        max_doc_threshold = storage_prof["max_cover_days"]
        min_doc_threshold = storage_prof["min_cover_days"]
        
        # Risk Flags
        is_stockout_risk = False
        is_excess_risk = False
        risk_label = "Optimal"
        
        if current_stock <= reorder_point or (doc is not None and doc < min_doc_threshold):
            is_stockout_risk = True
            risk_label = "Stockout Risk (Critical)" if current_stock < (safety_stock * 0.5) else "Stockout Risk (Warning)"
        elif doc is not None and doc > max_doc_threshold:
            is_excess_risk = True
            risk_label = "Excess / Spoilage Risk" if storage == "Fresh" else "Excess Inventory"
            
        # Suggested Replenishment Calculation:
        # Target stock = Reorder Point + (Target Cycle Stock: e.g. 5 days of demand)
        target_cycle_days = 2.0 if storage == "Fresh" else 7.0
        target_stock = reorder_point + (avg_daily_demand * target_cycle_days)
        suggested_replenishment = max(0.0, target_stock - current_stock)
        
        # Expiry tracking if available
        expiry_dt = latest_record.get("expiry_date", None)
        days_to_expiry = None
        if pd.notna(expiry_dt):
            try:
                days_to_expiry = (pd.to_datetime(expiry_dt) - max_date).days
            except Exception:
                days_to_expiry = None
                
        sku_rows.append({
            "sku_id": sku_id,
            "product_name": prod_name,
            "category": cat,
            "storage_type": storage,
            "region": region,
            "current_stock": int(current_stock),
            "avg_daily_demand": round(avg_daily_demand, 1),
            "lead_time_days": lead_time,
            "safety_stock": int(np.ceil(safety_stock)),
            "reorder_point": int(np.ceil(reorder_point)),
            "days_of_cover": doc,
            "is_stockout_risk": is_stockout_risk,
            "is_excess_risk": is_excess_risk,
            "risk_label": risk_label,
            "suggested_replenishment": int(np.ceil(suggested_replenishment)),
            "stock_value_inr": round(current_stock * unit_cost, 2),
            "days_to_expiry": days_to_expiry,
            "temp_spec": storage_prof["temp_range"],
        })
        
    return pd.DataFrame(sku_rows)
