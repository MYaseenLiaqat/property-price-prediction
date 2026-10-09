"""Benchmark and train the historical Lahore house-sale model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "processed" / "lahore_house_sale.csv"
MODEL_DIR = BASE / "models"
MODEL_PATH = MODEL_DIR / "lahore_house_sale_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
METADATA_PATH = MODEL_DIR / "lahore_house_sale_model_metadata.json"
RANDOM_STATE = 42


def build_preprocessor(categorical: list[str], numeric: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "location",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                numeric,
            ),
        ]
    )


def evaluate(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    residuals = predicted - actual
    return {
        "mae_pkr": float(mean_absolute_error(actual, predicted)),
        "rmse_pkr": float(mean_squared_error(actual, predicted) ** 0.5),
        "r2": float(r2_score(actual, predicted)),
        "median_absolute_error_pkr": float(median_absolute_error(actual, predicted)),
        "residual_mean_pkr": float(np.mean(residuals)),
        "residual_median_pkr": float(np.median(residuals)),
        "residual_std_pkr": float(np.std(residuals)),
        "residual_q05_pkr": float(np.quantile(residuals, 0.05)),
        "residual_q95_pkr": float(np.quantile(residuals, 0.95)),
        "absolute_error_q95_pkr": float(np.quantile(np.abs(residuals), 0.95)),
    }


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Processed dataset not found: {DATA}. Run scripts/prepare_lahore.py first.")

    data = pd.read_csv(DATA)
    required = {"price_pkr", "location", "area_sqft", "bedrooms", "bathrooms"}
    missing = required.difference(data.columns)
    if missing:
        raise SystemExit(f"Processed dataset is missing required columns: {sorted(missing)}")

    categorical = ["location"]
    numeric = ["area_sqft", "bedrooms", "bathrooms"]
    for optional in ["latitude", "longitude"]:
        if optional in data.columns and data[optional].notna().any():
            numeric.append(optional)

    features = data[categorical + numeric].copy()
    target = pd.to_numeric(data["price_pkr"], errors="coerce")
    usable = target.gt(0) & features["area_sqft"].gt(0)
    features = features.loc[usable].reset_index(drop=True)
    target = target.loc[usable].reset_index(drop=True)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )
    y_train_log = np.log1p(y_train)
    actual = y_test.to_numpy(dtype=float)

    regressors = {
        "median_baseline": DummyRegressor(strategy="median"),
        "random_forest": RandomForestRegressor(
            n_estimators=350,
            max_depth=28,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=350,
            max_depth=32,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }

    trained: dict[str, Pipeline] = {}
    results: dict[str, dict[str, float]] = {}
    predictions: dict[str, np.ndarray] = {}
    for name, regressor in regressors.items():
        pipeline = Pipeline(
            [
                ("preprocess", build_preprocessor(categorical, numeric)),
                ("model", regressor),
            ]
        )
        pipeline.fit(x_train, y_train_log)
        predicted = np.maximum(0, np.expm1(pipeline.predict(x_test)))
        trained[name] = pipeline
        predictions[name] = predicted
        results[name] = evaluate(actual, predicted)

    best_name = min(results, key=lambda name: results[name]["mae_pkr"])
    best_pipeline = trained[best_name]
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)

    timestamp = datetime.now(timezone.utc).isoformat()
    warning = (
        "This evaluation is a historical snapshot benchmark and is not evidence of current "
        "2026 predictive performance."
    )
    metrics = {
        "dataset_name": "lahore_house_sale.csv",
        "dataset_date": "2020-05-15",
        "evaluation_method": "random 80/20 train/test split",
        "random_state": RANDOM_STATE,
        "target_transform": "log1p(price_pkr), predictions converted back with expm1",
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "features": categorical + numeric,
        "results": results,
        "selected_model": best_name,
        "historical_data_warning": warning,
    }
    metadata = {
        "model_type": type(regressors[best_name]).__name__,
        "selected_model_name": best_name,
        "dataset_name": "lahore_house_sale.csv",
        "dataset_date": "2020-05-15",
        "training_timestamp_utc": timestamp,
        "feature_list": categorical + numeric,
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        **results[best_name],
        "preprocessing": {
            "target": "price_pkr",
            "target_transform": "log1p",
            "categorical": "location imputed with most frequent value and one-hot encoded",
            "numeric": "median imputation for area_sqft, bedrooms, bathrooms, latitude, longitude where present",
        },
        "held_out_error_statistics": {
            "model": best_name,
            "residual_definition": "predicted_price_minus_actual_price",
            **{key: value for key, value in results[best_name].items() if "residual" in key or "error_q95" in key},
        },
        "prediction_interval_status": "not_calibrated",
        "limitations": [
            warning,
            "The source is a historical listing snapshot with listings dated in 2019.",
            "Prices are asking prices, not verified transaction prices.",
            "Random splitting is used because no reliable current temporal validation frame exists.",
            "The model is a bootstrap benchmark and is not production-ready.",
        ],
        "historical_data_warning": warning,
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"selected_model": best_name, "results": results, "model": str(MODEL_PATH)}, indent=2))


if __name__ == "__main__":
    main()
