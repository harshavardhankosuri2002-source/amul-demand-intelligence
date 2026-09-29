"""
AMUL Synthetic Data Generator.
Generates reproducible, realistic distribution and demand data for Amul products.
Explicitly labeled as SYNTHETIC DEMO DATA for operational modeling and decision-support.
Produces both canonical and specific business columns:
revenue_inr, stock_closing_units, units_demanded_est, lost_sales_estimate,
stockout_flag, delivery_delay_flag, cold_chain_excursion_flag, festival_flag,
temperature_c, rainfall_mm, days_of_cover, and promotion metrics.
"""

from datetime import datetime, timedelta
import os
from typing import Dict, List
import numpy as np
import pandas as pd

# Definitive SKU Catalog across all 4 temperature regimes
SKU_CATALOG: List[Dict] = [
    # FRESH CATEGORY (Short Shelf Life: 2 to 15 days; Cold Chain: 2-4°C)
    {
        "sku_id": "AMUL-FRSH-001",
        "product_name": "Amul Taaza Toned Milk (1L Pouch)",
        "category": "Fresh Milk",
        "storage_type": "Fresh",
        "base_price": 54.0,
        "unit_cost": 46.0,
        "shelf_life_days": 2,
        "base_lead_time": 1,
        "daily_base_volume": 420,
        "promo_elasticity": 1.15,
        "moq": 50,
    },
    {
        "sku_id": "AMUL-FRSH-002",
        "product_name": "Amul Gold Full Cream Milk (500ml Pouch)",
        "category": "Fresh Milk",
        "storage_type": "Fresh",
        "base_price": 33.0,
        "unit_cost": 28.0,
        "shelf_life_days": 2,
        "base_lead_time": 1,
        "daily_base_volume": 580,
        "promo_elasticity": 1.10,
        "moq": 50,
    },
    {
        "sku_id": "AMUL-FRSH-003",
        "product_name": "Amul Masti Dahi (400g Cup)",
        "category": "Curd & Fermented",
        "storage_type": "Fresh",
        "base_price": 35.0,
        "unit_cost": 27.0,
        "shelf_life_days": 10,
        "base_lead_time": 2,
        "daily_base_volume": 210,
        "promo_elasticity": 1.30,
        "moq": 30,
    },
    {
        "sku_id": "AMUL-FRSH-004",
        "product_name": "Amul Fresh Malai Paneer (200g Block)",
        "category": "Fresh Dairy",
        "storage_type": "Fresh",
        "base_price": 92.0,
        "unit_cost": 74.0,
        "shelf_life_days": 14,
        "base_lead_time": 2,
        "daily_base_volume": 160,
        "promo_elasticity": 1.45,
        "moq": 20,
    },
    # CHILLED CATEGORY (Medium Shelf Life: 180 to 270 days; Cold Chain: 0-4°C)
    {
        "sku_id": "AMUL-CHIL-001",
        "product_name": "Amul Pasteurised Butter (500g Carton)",
        "category": "Butter",
        "storage_type": "Chilled",
        "base_price": 275.0,
        "unit_cost": 225.0,
        "shelf_life_days": 180,
        "base_lead_time": 4,
        "daily_base_volume": 190,
        "promo_elasticity": 1.55,
        "moq": 24,
    },
    {
        "sku_id": "AMUL-CHIL-002",
        "product_name": "Amul Processed Cheese Blocks (500g)",
        "category": "Cheese",
        "storage_type": "Chilled",
        "base_price": 290.0,
        "unit_cost": 235.0,
        "shelf_life_days": 240,
        "base_lead_time": 4,
        "daily_base_volume": 140,
        "promo_elasticity": 1.60,
        "moq": 20,
    },
    {
        "sku_id": "AMUL-CHIL-003",
        "product_name": "Amul Cheese Slices (200g 10 Slices)",
        "category": "Cheese",
        "storage_type": "Chilled",
        "base_price": 145.0,
        "unit_cost": 115.0,
        "shelf_life_days": 180,
        "base_lead_time": 3,
        "daily_base_volume": 175,
        "promo_elasticity": 1.40,
        "moq": 30,
    },
    # FROZEN CATEGORY (Deep Cold Chain: -18°C; Shelf Life: 360 days)
    {
        "sku_id": "AMUL-FROZ-001",
        "product_name": "Amul Real Ice Cream Vanilla Magic (1L Tub)",
        "category": "Ice Cream",
        "storage_type": "Frozen",
        "base_price": 160.0,
        "unit_cost": 118.0,
        "shelf_life_days": 360,
        "base_lead_time": 5,
        "daily_base_volume": 130,
        "promo_elasticity": 1.70,
        "moq": 15,
    },
    {
        "sku_id": "AMUL-FROZ-002",
        "product_name": "Amul Choco-Chips Ice Cream Tub (1L)",
        "category": "Ice Cream",
        "storage_type": "Frozen",
        "base_price": 240.0,
        "unit_cost": 175.0,
        "shelf_life_days": 360,
        "base_lead_time": 5,
        "daily_base_volume": 95,
        "promo_elasticity": 1.65,
        "moq": 15,
    },
    {
        "sku_id": "AMUL-FROZ-003",
        "product_name": "Amul Frozen Green Peas (500g Pouch)",
        "category": "Frozen Veg",
        "storage_type": "Frozen",
        "base_price": 85.0,
        "unit_cost": 62.0,
        "shelf_life_days": 365,
        "base_lead_time": 6,
        "daily_base_volume": 110,
        "promo_elasticity": 1.35,
        "moq": 25,
    },
    # AMBIENT CATEGORY (Ambient Warehouse; Shelf Life: 180 to 365 days)
    {
        "sku_id": "AMUL-AMBI-001",
        "product_name": "Amul Pure Cow Ghee (1L Tin)",
        "category": "Ghee",
        "storage_type": "Ambient",
        "base_price": 630.0,
        "unit_cost": 525.0,
        "shelf_life_days": 270,
        "base_lead_time": 6,
        "daily_base_volume": 120,
        "promo_elasticity": 1.80,
        "moq": 12,
    },
    {
        "sku_id": "AMUL-AMBI-002",
        "product_name": "Amul Kool Kesar Badam (200ml Can)",
        "category": "Beverages",
        "storage_type": "Ambient",
        "base_price": 35.0,
        "unit_cost": 26.0,
        "shelf_life_days": 180,
        "base_lead_time": 4,
        "daily_base_volume": 260,
        "promo_elasticity": 1.50,
        "moq": 48,
    },
    {
        "sku_id": "AMUL-AMBI-003",
        "product_name": "Amul Mithai Mate Sweetened Condensed Milk (400g)",
        "category": "Ambient Dairy",
        "storage_type": "Ambient",
        "base_price": 140.0,
        "unit_cost": 108.0,
        "shelf_life_days": 365,
        "base_lead_time": 5,
        "daily_base_volume": 85,
        "promo_elasticity": 1.90,
        "moq": 24,
    },
    {
        "sku_id": "AMUL-AMBI-004",
        "product_name": "Amul Dark Chocolate (150g Bar)",
        "category": "Chocolates",
        "storage_type": "Ambient",
        "base_price": 110.0,
        "unit_cost": 80.0,
        "shelf_life_days": 365,
        "base_lead_time": 5,
        "daily_base_volume": 105,
        "promo_elasticity": 1.60,
        "moq": 30,
    },
]

REGIONS = [
    {"region": "West Zone (Gujarat / MH)", "weight": 1.35, "base_temp": 32.0},
    {"region": "North Zone (Delhi NCR / PB)", "weight": 1.15, "base_temp": 34.0},
    {"region": "South Zone (KA / TN)", "weight": 0.85, "base_temp": 30.0},
    {"region": "East Zone (WB / Bihar)", "weight": 0.75, "base_temp": 31.0},
]


def generate_synthetic_amul_dataset(
    start_date: str = "2026-05-01",
    days: int = 150,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates a rich, highly realistic, reproducible distribution dataset.
    Produces both canonical fields and the specific fields expected:
    - revenue_inr AND revenue
    - stock_closing_units AND stock_on_hand
    - units_demanded_est AND lost_sales_estimate
    - stockout_flag, delivery_delay_flag, cold_chain_excursion_flag, festival_flag
    - temperature_c, rainfall_mm, days_of_cover, promotion_discount_pct, competitor_discount_pct
    """
    np.random.seed(seed)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    date_range = [start_dt + timedelta(days=i) for i in range(days)]

    rows = []

    # Track running inventory state across days for each (region, sku)
    running_inventory: Dict[str, int] = {}

    for dt in date_range:
        day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
        month = dt.month
        is_weekend = day_of_week in [5, 6]

        # Calendar factors
        is_summer = month in [5, 6, 7]
        is_monsoon = month in [7, 8, 9]
        is_festival = month in [8, 9, 10] or (dt.day in [14, 15] and month == 8) or (dt.day in [24, 25] and month == 10)
        festival_flag = 1 if is_festival else 0

        for reg in REGIONS:
            reg_name = reg["region"]
            reg_weight = reg["weight"]

            # Weather simulation
            temp_variation = np.sin((dt.timetuple().tm_yday / 365.0) * 2 * np.pi) * 6.0
            temperature_c = round(reg["base_temp"] + temp_variation + np.random.normal(0, 1.5), 1)
            rainfall_mm = round(max(0.0, np.random.exponential(12.0) if is_monsoon else np.random.exponential(1.5)), 1)

            # Cold chain excursion risk increases with high ambient temperature (>35°C) and logistics delays
            excursion_prob = 0.08 if temperature_c > 35 else 0.02
            cold_chain_excursion = 1 if np.random.rand() < excursion_prob else 0

            for sku in SKU_CATALOG:
                key = f"{reg_name}_{sku['sku_id']}"
                cat = sku["category"]
                storage = sku["storage_type"]

                # Promotion assignment
                is_promo = 1 if np.random.rand() < 0.12 else 0
                promo_discount = np.random.choice([0.05, 0.10, 0.15]) if is_promo else 0.0
                promo_discount_pct = round(promo_discount * 100, 1)
                competitor_discount_pct = round(np.random.choice([0.0, 5.0, 10.0, 12.0]) if np.random.rand() < 0.20 else 0.0, 1)

                selling_price = round(sku["base_price"] * (1.0 - promo_discount), 2)

                # Base unconstrained demand calculation
                volume = sku["daily_base_volume"] * reg_weight

                # Seasonality & Weather elasticity
                if cat in ["Ice Cream", "Beverages"]:
                    if temperature_c > 32:
                        volume *= (1.0 + (temperature_c - 32) * 0.04)
                    if is_weekend:
                        volume *= 1.30
                elif cat in ["Ghee", "Ambient Dairy"]:
                    if is_festival:
                        volume *= 1.65
                    if is_weekend:
                        volume *= 1.15
                elif cat in ["Butter", "Cheese"]:
                    if is_weekend:
                        volume *= 1.30
                    if is_festival:
                        volume *= 1.25
                elif cat in ["Fresh Milk", "Curd & Fermented"]:
                    volume *= 1.06 if is_weekend else 0.98

                # Promotion lift
                if is_promo:
                    volume *= (sku["promo_elasticity"] + np.random.uniform(0.05, 0.15))

                # Competitor discount effect
                if competitor_discount_pct > promo_discount_pct:
                    volume *= 0.88

                noise = np.random.normal(1.0, 0.10)
                demanded_units = max(0, int(volume * noise))

                # Opening stock
                if key not in running_inventory:
                    # Initialize initial stock based on category
                    if storage == "Fresh":
                        running_inventory[key] = int(demanded_units * np.random.uniform(1.5, 2.5))
                    elif storage == "Chilled":
                        running_inventory[key] = int(demanded_units * np.random.uniform(8.0, 18.0))
                    elif storage == "Frozen":
                        running_inventory[key] = int(demanded_units * np.random.uniform(10.0, 22.0))
                    else:
                        running_inventory[key] = int(demanded_units * np.random.uniform(15.0, 32.0))

                stock_opening = running_inventory[key]

                # Delivery delays (weather, monsoon, or random logistics bottlenecks)
                delay_prob = 0.18 if rainfall_mm > 25.0 else 0.06
                delivery_delay_flag = 1 if np.random.rand() < delay_prob else 0
                lead_time = sku["base_lead_time"] + (2 if delivery_delay_flag else 0)

                # Periodic replenishment arrival
                replenishment_units = 0
                if stock_opening <= (demanded_units * (lead_time + 1)):
                    # Replenishment batch triggered
                    replenishment_units = int(demanded_units * (lead_time + 4))
                elif np.random.rand() < 0.15:
                    replenishment_units = int(demanded_units * (lead_time + 2))

                total_available = stock_opening + replenishment_units

                # Fulfillment & Stockout logic
                if demanded_units > total_available:
                    units_sold = total_available
                    lost_sales = demanded_units - total_available
                    stockout_flag = 1
                    stock_closing = 0
                else:
                    units_sold = demanded_units
                    lost_sales = 0
                    stockout_flag = 0
                    stock_closing = total_available - units_sold

                # Wastage & Expiry
                units_wasted = 0
                if storage == "Fresh":
                    # Spoilage probability increases if cold chain excursion occurred
                    w_rate = 0.06 if cold_chain_excursion else 0.02
                    if np.random.rand() < 0.30:
                        units_wasted = int(stock_closing * w_rate)
                        stock_closing = max(0, stock_closing - units_wasted)
                elif storage == "Chilled" and cold_chain_excursion:
                    units_wasted = int(stock_closing * 0.03)
                    stock_closing = max(0, stock_closing - units_wasted)

                # Update running inventory for next day
                running_inventory[key] = stock_closing

                # Days of cover calculation
                doc = round(float(stock_closing / demanded_units), 1) if demanded_units > 0 else 99.0
                revenue = round(units_sold * selling_price, 2)
                expiry_dt = dt + timedelta(days=sku["shelf_life_days"])

                rows.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "sku_id": sku["sku_id"],
                    "product_name": sku["product_name"],
                    "category": sku["category"],
                    "storage_type": storage,
                    "region": reg_name,
                    "units_sold": units_sold,
                    "units_demanded_est": demanded_units,
                    "lost_sales_estimate": lost_sales,
                    "stock_opening_units": stock_opening,
                    "stock_closing_units": stock_closing,
                    "stock_on_hand": stock_closing,  # Canonical alias
                    "replenishment_units": replenishment_units,
                    "lead_time_days": lead_time,
                    "delivery_delay_flag": delivery_delay_flag,
                    "stockout_flag": stockout_flag,
                    "units_wasted": units_wasted,
                    "shelf_life_days": sku["shelf_life_days"],
                    "cold_chain_excursion_flag": cold_chain_excursion,
                    "promotion_flag": is_promo,
                    "promotion_discount_pct": promo_discount_pct,
                    "competitor_discount_pct": competitor_discount_pct,
                    "festival_flag": festival_flag,
                    "temperature_c": temperature_c,
                    "rainfall_mm": rainfall_mm,
                    "days_of_cover": doc,
                    "selling_price": selling_price,
                    "revenue_inr": revenue,
                    "revenue": revenue,  # Canonical alias
                    "unit_cost": sku["unit_cost"],
                    "expiry_date": expiry_dt.strftime("%Y-%m-%d"),
                    "data_type": "SYNTHETIC_DEMO",
                    "data_source_flag": "SYNTHETIC_DEMO",
                })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"])
    return df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("Generating comprehensive Amul distribution dataset...")
    df_sample = generate_synthetic_amul_dataset(days=150)
    csv_path = "data/sample_amul_distribution_data.csv"
    df_sample.to_csv(csv_path, index=False)
    print(f"Generated {len(df_sample):,} rows with {len(df_sample.columns)} columns into {csv_path}")
