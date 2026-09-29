"""
AMUL Demand Forecasting Engine.
Implements:
1. Chronological time-series train/test split (no lookahead data leakage).
2. Baseline Model: 7-day Rolling Average / Seasonal Naive lag-7.
3. Machine Learning Model: GradientBoosting / RandomForest / Ridge with feature engineering:
   - Calendar features: Day of week, Month, Day of month, Is Weekend.
   - Lag features: Lag 1, Lag 7, Lag 14.
   - Rolling features: 7-day and 14-day rolling means.
   - Exogenous features: Promotion flag, Selling price.
4. Evaluation Metrics: MAE, RMSE, WAPE (strictly safe against zero-demand denominators).
5. Multi-step recursive/direct horizon prediction with residual prediction intervals.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


def calculate_wape(actual: np.ndarray, predicted: np.ndarray) -> Optional[float]:
    """
    Weighted Absolute Percentage Error (WAPE).
    WAPE = sum(|actual - predicted|) / sum(actual)
    If sum(actual) == 0: returns None (mathematically undefined/zero demand denominator).
    """
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    
    total_actual = np.sum(actual)
    if total_actual == 0:
        return None
    
    total_abs_error = np.sum(np.abs(actual - predicted))
    return float(total_abs_error / total_actual)


def evaluate_forecast(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, Optional[float]]:
    """
    Computes standard enterprise forecast metrics: MAE, RMSE, and WAPE.
    """
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    
    if len(actual) == 0:
        return {"mae": None, "rmse": None, "wape": None, "samples": 0}
        
    mae = float(mean_absolute_error(actual, predicted))
    rmse = float(root_mean_squared_error(actual, predicted))
    wape = calculate_wape(actual, predicted)
    
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "wape": round(wape * 100, 2) if wape is not None else None,  # Expressed as percentage
        "samples": len(actual),
    }


def create_time_series_features(df_series: pd.DataFrame) -> pd.DataFrame:
    """
    Builds lag, rolling, and calendar features from an aggregated daily time series.
    Requires columns: ['date', 'units_sold'] and optional ['promotion_flag', 'selling_price'].
    """
    df = df_series.copy().sort_values("date").reset_index(drop=True)
    
    # Calendar features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    
    # Lag features
    df["lag_1"] = df["units_sold"].shift(1)
    df["lag_7"] = df["units_sold"].shift(7)
    df["lag_14"] = df["units_sold"].shift(14)
    
    # Rolling window statistics (shifted to prevent leakage)
    df["rolling_mean_7"] = df["units_sold"].shift(1).rolling(window=7, min_periods=1).mean()
    df["rolling_std_7"] = df["units_sold"].shift(1).rolling(window=7, min_periods=1).std().fillna(0)
    df["rolling_mean_14"] = df["units_sold"].shift(1).rolling(window=14, min_periods=1).mean()
    
    if "promotion_flag" not in df.columns:
        df["promotion_flag"] = 0
    if "selling_price" not in df.columns:
        df["selling_price"] = 0.0
        
    return df


def train_and_evaluate_models(
    df_series: pd.DataFrame,
    test_days: int = 14,
    model_type: str = "GradientBoosting",
) -> Tuple[Dict, pd.DataFrame, object, Dict]:
    """
    Performs chronological train/test split.
    Trains both:
    1. Baseline Model: 7-day Seasonal Naive / Moving Average
    2. ML Model (GradientBoosting, RandomForest, or Ridge)
    Evaluates both on the held-out test split.
    """
    df_feat = create_time_series_features(df_series)
    
    # Drop warm-up rows where lag_14 is NaN
    valid_df = df_feat.dropna(subset=["lag_14"]).reset_index(drop=True)
    if len(valid_df) <= test_days + 7:
        # Not enough data for split
        return {}, pd.DataFrame(), None, {"error": "Insufficient historical points for train/test split."}
        
    train_df = valid_df.iloc[:-test_days].copy()
    test_df = valid_df.iloc[-test_days:].copy()
    
    feature_cols = [
        "day_of_week",
        "month",
        "day",
        "is_weekend",
        "lag_1",
        "lag_7",
        "lag_14",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_14",
        "promotion_flag",
        "selling_price",
    ]
    
    X_train = train_df[feature_cols]
    y_train = train_df["units_sold"]
    X_test = test_df[feature_cols]
    y_test = test_df["units_sold"]
    
    # 1. Baseline Model: Seasonal Naive (Lag 7) with 7-day Moving Average fallback
    y_pred_baseline = test_df["lag_7"].fillna(test_df["rolling_mean_7"]).to_numpy()
    baseline_metrics = evaluate_forecast(y_test.to_numpy(), y_pred_baseline)
    
    # 2. ML Model selection
    if model_type == "RandomForest":
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=6)
    elif model_type == "Ridge":
        model = Ridge(alpha=1.0)
    else:
        model = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
        
    model.fit(X_train, y_train)
    y_pred_ml = np.clip(model.predict(X_test), 0, None)
    ml_metrics = evaluate_forecast(y_test.to_numpy(), y_pred_ml)
    
    # Evaluation comparison summary
    comparison = {
        "baseline_mae": baseline_metrics["mae"],
        "baseline_rmse": baseline_metrics["rmse"],
        "baseline_wape": baseline_metrics["wape"],
        "ml_mae": ml_metrics["mae"],
        "ml_rmse": ml_metrics["rmse"],
        "ml_wape": ml_metrics["wape"],
        "wape_delta": (
            round(baseline_metrics["wape"] - ml_metrics["wape"], 2)
            if (baseline_metrics["wape"] is not None and ml_metrics["wape"] is not None)
            else None
        ),
        "test_days": test_days,
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "model_name": model_type,
    }
    
    test_eval_df = test_df[["date", "units_sold"]].copy()
    test_eval_df["baseline_forecast"] = y_pred_baseline
    test_eval_df["ml_forecast"] = np.round(y_pred_ml, 1)
    
    # Feature importance if available
    importance = {}
    if hasattr(model, "feature_importances_"):
        importance = dict(zip(feature_cols, [round(float(v), 4) for v in model.feature_importances_]))
        
    return comparison, test_eval_df, model, importance


def generate_future_forecast(
    df_series: pd.DataFrame,
    horizon_days: int = 14,
    model_type: str = "GradientBoosting",
) -> pd.DataFrame:
    """
    Generates out-of-sample forward-looking forecast for the requested horizon (e.g. 7, 14, 21, 30 days).
    Produces predicted mean and 80% prediction interval [lower_bound, upper_bound].
    """
    df_feat = create_time_series_features(df_series)
    valid_df = df_feat.dropna(subset=["lag_14"]).reset_index(drop=True)
    if len(valid_df) < 14:
        return pd.DataFrame()
        
    feature_cols = [
        "day_of_week",
        "month",
        "day",
        "is_weekend",
        "lag_1",
        "lag_7",
        "lag_14",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_14",
        "promotion_flag",
        "selling_price",
    ]
    
    X_all = valid_df[feature_cols]
    y_all = valid_df["units_sold"]
    
    # Train full model
    if model_type == "RandomForest":
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=6)
    else:
        model = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
    model.fit(X_all, y_all)
    
    # Estimate residual variance for prediction interval
    in_sample_preds = model.predict(X_all)
    residuals = y_all - in_sample_preds
    residual_std = float(np.std(residuals))
    
    # Recursive multi-step forecasting
    current_history = valid_df[["date", "units_sold", "promotion_flag", "selling_price"]].copy()
    last_date = current_history["date"].max()
    avg_price = current_history["selling_price"].iloc[-7:].mean()
    
    future_rows = []
    
    for step in range(1, horizon_days + 1):
        next_date = last_date + pd.Timedelta(days=step)
        
        # Build features for next_date using past history
        units_series = current_history["units_sold"]
        lag_1 = units_series.iloc[-1]
        lag_7 = units_series.iloc[-7] if len(units_series) >= 7 else lag_1
        lag_14 = units_series.iloc[-14] if len(units_series) >= 14 else lag_7
        roll_7 = units_series.iloc[-7:].mean()
        roll_std_7 = units_series.iloc[-7:].std() if len(units_series) >= 7 else 0.0
        roll_14 = units_series.iloc[-14:].mean() if len(units_series) >= 14 else roll_7
        
        step_features = pd.DataFrame([{
            "day_of_week": next_date.dayofweek,
            "month": next_date.month,
            "day": next_date.day,
            "is_weekend": 1 if next_date.dayofweek in [5, 6] else 0,
            "lag_1": lag_1,
            "lag_7": lag_7,
            "lag_14": lag_14,
            "rolling_mean_7": roll_7,
            "rolling_std_7": roll_std_7 if not np.isnan(roll_std_7) else 0.0,
            "rolling_mean_14": roll_14,
            "promotion_flag": 0,
            "selling_price": avg_price,
        }])
        
        pred_val = max(0.0, float(model.predict(step_features[feature_cols])[0]))
        
        # 80% Prediction interval: z=1.28 * std * sqrt(1 + 0.05 * step)
        interval_margin = 1.28 * residual_std * np.sqrt(1.0 + 0.05 * step)
        lower_bound = max(0.0, round(pred_val - interval_margin, 1))
        upper_bound = max(lower_bound, round(pred_val + interval_margin, 1))
        
        future_rows.append({
            "date": next_date,
            "forecast_demand": round(pred_val, 1),
            "lower_interval_80": lower_bound,
            "upper_interval_80": upper_bound,
            "baseline_reference": round(roll_7, 1),
        })
        
        # Append simulated row to history for recursive rolling
        new_row = pd.DataFrame([{
            "date": next_date,
            "units_sold": pred_val,
            "promotion_flag": 0,
            "selling_price": avg_price,
        }])
        current_history = pd.concat([current_history, new_row], ignore_index=True)
        
    return pd.DataFrame(future_rows)
