"""
Automated unit tests for data validation, cleaning, and schema mapping.
"""

import pandas as pd
import pytest
from src.data_loader import REQUIRED_FIELDS, validate_and_clean_data


def test_validation_detects_missing_required_fields():
    # DataFrame missing 'units_sold' and 'stock_on_hand'
    bad_df = pd.DataFrame({
        "date": ["2026-06-01", "2026-06-02"],
        "sku_id": ["AMUL-001", "AMUL-001"],
        "product_name": ["Amul Taaza", "Amul Taaza"],
        "category": ["Fresh Milk", "Fresh Milk"],
    })
    
    cleaned, missing, warnings = validate_and_clean_data(bad_df)
    assert "units_sold" in missing
    assert "stock_on_hand" in missing
    assert len(missing) == 2


def test_validation_applies_column_mapping():
    # External system with legacy column naming
    legacy_df = pd.DataFrame({
        "TransDate": ["2026-06-01", "2026-06-02"],
        "MaterialNumber": ["AMUL-001", "AMUL-001"],
        "Description": ["Amul Taaza 1L", "Amul Taaza 1L"],
        "ProdGroup": ["Fresh Milk", "Fresh Milk"],
        "QtyDispatched": [150, 200],
        "DepotStock": [400, 350],
    })
    
    mapping = {
        "TransDate": "date",
        "MaterialNumber": "sku_id",
        "Description": "product_name",
        "ProdGroup": "category",
        "QtyDispatched": "units_sold",
        "DepotStock": "stock_on_hand",
    }
    
    cleaned, missing, warnings = validate_and_clean_data(legacy_df, column_mapping=mapping)
    assert len(missing) == 0
    assert "units_sold" in cleaned.columns
    assert "stock_on_hand" in cleaned.columns
    assert cleaned["units_sold"].iloc[0] == 150


def test_validation_clips_negative_numbers():
    df_with_negatives = pd.DataFrame({
        "date": ["2026-06-01"],
        "sku_id": ["AMUL-001"],
        "product_name": ["Amul Taaza"],
        "category": ["Fresh Milk"],
        "units_sold": [-50],  # Corrupt negative entry
        "stock_on_hand": [-10],
    })
    
    cleaned, missing, warnings = validate_and_clean_data(df_with_negatives)
    assert len(missing) == 0
    assert cleaned["units_sold"].iloc[0] == 0  # Clipped to zero
    assert cleaned["stock_on_hand"].iloc[0] == 0
    assert any("negative" in w.lower() for w in warnings)


def test_storage_type_inferred_when_missing():
    df_no_storage = pd.DataFrame({
        "date": ["2026-06-01"],
        "sku_id": ["AMUL-001"],
        "product_name": ["Amul Taaza 1L"],
        "category": ["Fresh Milk"],
        "units_sold": [100],
        "stock_on_hand": [200],
    })
    
    cleaned, missing, warnings = validate_and_clean_data(df_no_storage)
    assert cleaned["storage_type"].iloc[0] == "Fresh"
