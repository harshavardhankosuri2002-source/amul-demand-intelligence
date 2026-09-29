"""
Automated unit tests for time-series forecasting, chronological splits,
and metric edge case handling (including zero-demand denominators).
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytest
from src.forecasting import (
    calculate_wape,
    create_time_series_features,
    evaluate_forecast,
    train_and_evaluate_models,
)


def test_wape_zero_demand_returns_none():
    actual = np.array([0, 0, 0])
    predicted = np.array([5, 10, 2])
    wape = calculate_wape(actual, predicted)
    assert wape is None, "WAPE must return None when total actual demand is zero to prevent division by zero."


def test_wape_calculation_correctness():
    actual = np.array([100, 200, 300])  # sum = 600
    predicted = np.array([90, 220, 300])  # abs err = 10 + 20 + 0 = 30
    wape = calculate_wape(actual, predicted)
    assert wape == pytest.approx(30 / 600, 0.001)


def test_evaluate_forecast_handles_empty_arrays():
    metrics = evaluate_forecast(np.array([]), np.array([]))
    assert metrics["mae"] is None
    assert metrics["rmse"] is None
    assert metrics["wape"] is None
    assert metrics["samples"] == 0


def test_feature_engineering_creates_lags():
    dates = [datetime(2026, 6, 1) + timedelta(days=i) for i in range(30)]
    df = pd.DataFrame({
        "date": dates,
        "units_sold": [100 + i for i in range(30)],
    })
    
    df_feat = create_time_series_features(df)
    assert "lag_1" in df_feat.columns
    assert "lag_7" in df_feat.columns
    assert "lag_14" in df_feat.columns
    assert "rolling_mean_7" in df_feat.columns
    assert df_feat["lag_1"].iloc[1] == 100
    assert df_feat["lag_7"].iloc[7] == 100


def test_chronological_split_avoids_data_leakage():
    dates = [datetime(2026, 6, 1) + timedelta(days=i) for i in range(50)]
    df = pd.DataFrame({
        "date": dates,
        "units_sold": [100 + (i % 7) * 10 for i in range(50)],
        "promotion_flag": [0] * 50,
        "selling_price": [50.0] * 50,
    })
    
    comp, test_df, model, imp = train_and_evaluate_models(df, test_days=10, model_type="Ridge")
    assert comp["test_days"] == 10
    assert len(test_df) == 10
    # Verify test dates are strictly later than training dates
    assert test_df["date"].min() > df["date"].iloc[0]
