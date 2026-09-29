"""
AMUL Data Ingestion, Schema Normalization, and Data Quality Layer.
Handles canonical schema mappings, robust alias detection, data hygiene,
and graceful degradation for optional analytical fields.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Core required fields for minimal dashboard functionality
REQUIRED_FIELDS = [
    "date",
    "sku_id",
    "product_name",
    "category",
    "units_sold",
    "stock_on_hand",
]

# Analytical optional fields that enhance specific modules
OPTIONAL_FIELDS = [
    "revenue",
    "units_demanded_est",
    "lost_sales_estimate",
    "stock_opening_units",
    "stock_closing_units",
    "replenishment_units",
    "lead_time_days",
    "delivery_delay_flag",
    "stockout_flag",
    "units_wasted",
    "shelf_life_days",
    "cold_chain_excursion_flag",
    "promotion_flag",
    "promotion_discount_pct",
    "competitor_discount_pct",
    "festival_flag",
    "temperature_c",
    "rainfall_mm",
    "days_of_cover",
    "data_type",
    "storage_type",
    "region",
    "distributor_id",
    "retailer_id",
    "channel",
    "selling_price",
    "unit_cost",
    "expiry_date",
    "data_source_flag",
]

# Canonical Aliases mapping: Target Canonical Column -> List of known historical / alternative column names
KNOWN_ALIASES: Dict[str, List[str]] = {
    "revenue": [
        "revenue_inr",
        "sales_inr",
        "total_revenue",
        "revenue_rs",
        "sales_amount",
        "sales_revenue",
        "rev_inr",
        "rev",
    ],
    "stock_on_hand": [
        "stock_closing_units",
        "closing_stock",
        "current_stock",
        "stock_units",
        "inventory_units",
        "ending_inventory",
        "soh",
    ],
    "date": [
        "trans_date",
        "transaction_date",
        "day",
        "order_date",
        "invoice_date",
        "dispatch_date",
    ],
    "units_sold": [
        "sales_units",
        "quantity_sold",
        "qty_sold",
        "sales_volume",
        "volume_sold",
        "qty",
        "units",
    ],
    "sku_id": [
        "sku",
        "product_id",
        "material_number",
        "item_code",
        "sku_code",
    ],
    "product_name": [
        "product",
        "item_name",
        "description",
        "sku_name",
        "material_desc",
    ],
    "category": [
        "product_category",
        "prod_group",
        "sub_category",
        "cat",
    ],
    "region": [
        "zone",
        "territory",
        "market",
        "location",
        "sales_zone",
    ],
    "units_demanded_est": [
        "units_demanded",
        "demand_units",
        "estimated_demand",
        "demanded_units",
        "demand_est",
        "unconstrained_demand",
    ],
    "lost_sales_estimate": [
        "lost_sales",
        "unserved_demand",
        "unmet_demand",
        "stockout_lost_units",
    ],
    "units_wasted": [
        "wasted_units",
        "spoilage_units",
        "damaged_units",
        "expired_units",
        "wastage",
    ],
    "lead_time_days": [
        "lead_time",
        "lt_days",
        "replenishment_lead_time",
    ],
    "stockout_flag": [
        "is_stockout",
        "stockout",
        "stock_out_flag",
    ],
    "delivery_delay_flag": [
        "delay_flag",
        "is_delayed",
        "transit_delay_flag",
    ],
    "cold_chain_excursion_flag": [
        "temp_excursion_flag",
        "cold_chain_breach",
        "temperature_breach_flag",
    ],
    "festival_flag": [
        "is_festival",
        "holiday_flag",
        "festive_flag",
    ],
    "promotion_flag": [
        "is_promo",
        "promo_flag",
        "promotion",
    ],
    "selling_price": [
        "price",
        "unit_price",
        "mrp",
        "rate",
    ],
    "unit_cost": [
        "cost_price",
        "transfer_price",
        "cogs_unit",
        "cost",
    ],
    "shelf_life_days": [
        "shelf_life",
        "expiry_period_days",
    ],
}

DEFAULT_STORAGE_BY_CATEGORY = {
    "Fresh Milk": "Fresh",
    "Curd & Fermented": "Fresh",
    "Fresh Dairy": "Fresh",
    "Butter": "Chilled",
    "Cheese": "Chilled",
    "Ice Cream": "Frozen",
    "Frozen Veg": "Frozen",
    "Ghee": "Ambient",
    "Beverages": "Ambient",
    "Ambient Dairy": "Ambient",
    "Chocolates": "Ambient",
}


def normalize_column_name(col: str) -> str:
    """Normalizes a raw column name to lowercase trimmed snake_case."""
    return str(col).strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")


def validate_and_clean_data(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None,
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Normalizes, validates, and cleans the input supply-chain dataset.
    Features:
    1. Automatic alias mapping without overwriting valid canonical columns.
    2. Strict preservation of original aliases (e.g. keeps both revenue_inr and revenue).
    3. Missing required columns check with plain language reporting.
    4. Coercion of date, numeric types, and negative value clipping with warnings.
    5. Fallback inference of revenue, selling price, and storage category.
    """
    if df.empty:
        return df.copy(), REQUIRED_FIELDS.copy(), ["The uploaded dataset is empty."]

    cleaned = df.copy()
    warnings: List[str] = []

    # 1. Standardize column headers
    cleaned.columns = [normalize_column_name(c) for c in cleaned.columns]

    # 2. Apply user-supplied manual mapping first, if provided
    if column_mapping:
        norm_user_mapping = {
            normalize_column_name(k): normalize_column_name(v)
            for k, v in column_mapping.items()
        }
        for orig, target in norm_user_mapping.items():
            if orig in cleaned.columns and orig != target:
                if target not in cleaned.columns or cleaned[target].isna().all():
                    cleaned[target] = cleaned[orig]
                    warnings.append(f"Applied custom mapping: '{orig}' -> '{target}'.")

    # 3. Automatic alias resolution for canonical fields
    for canonical_col, aliases in KNOWN_ALIASES.items():
        # Only populate canonical column if it's currently missing or entirely null
        if canonical_col not in cleaned.columns or cleaned[canonical_col].isna().all():
            for alias in aliases:
                norm_alias = normalize_column_name(alias)
                if norm_alias in cleaned.columns and not cleaned[norm_alias].isna().all():
                    cleaned[canonical_col] = cleaned[norm_alias]
                    warnings.append(
                        f"Mapped alias column '{norm_alias}' to canonical field '{canonical_col}'."
                    )
                    break

    # 4. Check for required columns
    missing_required = [col for col in REQUIRED_FIELDS if col not in cleaned.columns]
    if missing_required:
        readable_missing = ", ".join([f"'{c}'" for c in missing_required])
        warnings.append(f"CRITICAL: Missing mandatory columns: {readable_missing}.")
        return cleaned, missing_required, warnings

    # 5. Coerce and validate date column
    try:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
        bad_dates = int(cleaned["date"].isna().sum())
        if bad_dates > 0:
            warnings.append(f"Coerced {bad_dates:,} unparseable date entries; dropped invalid rows.")
            cleaned = cleaned.dropna(subset=["date"])
    except Exception as e:
        warnings.append(f"Date conversion error: {str(e)}")
        return cleaned, ["date"], warnings

    # 6. Numeric sanitization and negative value handling
    numeric_columns = [
        "units_sold",
        "stock_on_hand",
        "revenue",
        "units_demanded_est",
        "lost_sales_estimate",
        "stock_opening_units",
        "stock_closing_units",
        "replenishment_units",
        "lead_time_days",
        "units_wasted",
        "shelf_life_days",
        "promotion_discount_pct",
        "competitor_discount_pct",
        "temperature_c",
        "rainfall_mm",
        "days_of_cover",
        "selling_price",
        "unit_cost",
    ]

    for col in numeric_columns:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0)
            # Clip negative values for quantities and prices (exclude temperature which can be negative)
            if col not in ["temperature_c"]:
                neg_count = int((cleaned[col] < 0).sum())
                if neg_count > 0:
                    warnings.append(f"Column '{col}' contained {neg_count:,} negative entries; clipped to 0.")
                    cleaned[col] = cleaned[col].clip(lower=0)

    # Boolean / flag normalization (0 or 1)
    flag_columns = [
        "stockout_flag",
        "delivery_delay_flag",
        "cold_chain_excursion_flag",
        "festival_flag",
        "promotion_flag",
    ]
    for col in flag_columns:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).astype(int).clip(0, 1)

    # 7. Derived canonical fallbacks and optional inferences
    # Revenue fallback from selling_price * units_sold
    if "revenue" not in cleaned.columns or cleaned["revenue"].sum() == 0:
        if "selling_price" in cleaned.columns and cleaned["selling_price"].sum() > 0:
            cleaned["revenue"] = cleaned["units_sold"] * cleaned["selling_price"]
            warnings.append("Computed canonical 'revenue' as (units_sold * selling_price).")
        elif "revenue_inr" in cleaned.columns:
            cleaned["revenue"] = pd.to_numeric(cleaned["revenue_inr"], errors="coerce").fillna(0)
        else:
            cleaned["revenue"] = 0.0
            warnings.append("Notice: 'revenue' not provided. Defaulted to 0.0 (revenue analytics disabled).")

    # Selling price fallback from revenue / units_sold
    if "selling_price" not in cleaned.columns or cleaned["selling_price"].sum() == 0:
        if "revenue" in cleaned.columns and cleaned["units_sold"].sum() > 0:
            safe_units = cleaned["units_sold"].replace(0, np.nan)
            cleaned["selling_price"] = (cleaned["revenue"] / safe_units).fillna(0).round(2)

    # Storage type inference
    if "storage_type" not in cleaned.columns:
        cleaned["storage_type"] = cleaned["category"].map(DEFAULT_STORAGE_BY_CATEGORY).fillna("Ambient")
        warnings.append("Inferred 'storage_type' from product category taxonomy.")

    # Region fallback
    if "region" not in cleaned.columns:
        cleaned["region"] = "National / All Zones"

    # Lead time fallback
    if "lead_time_days" not in cleaned.columns:
        cleaned["lead_time_days"] = 3
        warnings.append("Defaulted missing 'lead_time_days' to 3 days.")

    # Units wasted fallback
    if "units_wasted" not in cleaned.columns:
        cleaned["units_wasted"] = 0

    # Stock closing units alias sync
    if "stock_closing_units" not in cleaned.columns and "stock_on_hand" in cleaned.columns:
        cleaned["stock_closing_units"] = cleaned["stock_on_hand"]
    elif "stock_on_hand" not in cleaned.columns and "stock_closing_units" in cleaned.columns:
        cleaned["stock_on_hand"] = cleaned["stock_closing_units"]

    # Revenue INR alias sync
    if "revenue_inr" not in cleaned.columns and "revenue" in cleaned.columns:
        cleaned["revenue_inr"] = cleaned["revenue"]

    # Units demanded estimate fallback
    if "units_demanded_est" not in cleaned.columns:
        lost_sales = cleaned["lost_sales_estimate"] if "lost_sales_estimate" in cleaned.columns else 0
        cleaned["units_demanded_est"] = cleaned["units_sold"] + lost_sales

    # Lost sales fallback
    if "lost_sales_estimate" not in cleaned.columns:
        if "stockout_flag" in cleaned.columns:
            # Simple heuristic when lost sales not explicitly logged
            cleaned["lost_sales_estimate"] = np.where(cleaned["stockout_flag"] == 1, cleaned["units_sold"] * 0.25, 0.0)
        else:
            cleaned["lost_sales_estimate"] = 0.0

    # Data type tag
    if "data_type" not in cleaned.columns:
        cleaned["data_type"] = cleaned.get("data_source_flag", "SYNTHETIC_DEMO")

    # Chronological sort
    cleaned = cleaned.sort_values(by=["date", "sku_id"]).reset_index(drop=True)
    return cleaned, [], warnings


def get_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates a comprehensive data hygiene and quality diagnostic report.
    Used for Module 8 (Data Quality) and Section 4 of the PDF report.
    """
    if df.empty:
        return {
            "total_rows": 0,
            "total_columns": 0,
            "duplicate_rows": 0,
            "date_range": "N/A",
            "sku_count": 0,
            "category_count": 0,
            "region_count": 0,
            "columns_summary": pd.DataFrame(),
            "overall_health_score": 0,
        }

    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated(subset=["date", "sku_id", "region"]).sum()) if {"date", "sku_id", "region"}.issubset(df.columns) else int(df.duplicated().sum())

    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range_str = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}" if pd.notna(min_date) else "N/A"

    sku_count = int(df["sku_id"].nunique()) if "sku_id" in df.columns else 0
    cat_count = int(df["category"].nunique()) if "category" in df.columns else 0
    reg_count = int(df["region"].nunique()) if "region" in df.columns else 0

    col_stats = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = round((null_count / total_rows) * 100, 2)
        dtype = str(df[col].dtype)
        unique_cnt = int(df[col].nunique())
        is_numeric = pd.api.types.is_numeric_dtype(df[col])
        neg_count = int((df[col] < 0).sum()) if is_numeric else 0

        col_stats.append({
            "Column Name": col,
            "Data Type": dtype,
            "Distinct Values": unique_cnt,
            "Null Count": null_count,
            "Null %": null_pct,
            "Negative Values": neg_count,
            "Status": "✅ OK" if null_count == 0 and neg_count == 0 else "⚠️ Notice",
        })

    col_summary_df = pd.DataFrame(col_stats)

    # Health score (100 minus penalty for nulls, duplicates, and negatives)
    penalty = (duplicate_rows / max(1, total_rows)) * 40 + (col_summary_df["Null %"].mean()) * 0.5
    health_score = max(50, min(100, int(100 - penalty)))

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "date_range": date_range_str,
        "sku_count": sku_count,
        "category_count": cat_count,
        "region_count": reg_count,
        "columns_summary": col_summary_df,
        "overall_health_score": health_score,
    }
