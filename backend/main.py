import json
import os
from pathlib import Path

import joblib
import uvicorn
import pandas as pd
import numpy as np

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse


BASE = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE / "models" / "lahore_house_sale_model.joblib"
METADATA_PATH = BASE / "models" / "lahore_house_sale_model_metadata.json"
METRICS_PATH = BASE / "models" / "metrics.json"
DATA_REPORT_PATH = BASE / "data" / "reference" / "lahore_house_sale_data_report.json"
FRONTEND_PATH = BASE / "frontend"

MODEL = None
MODEL_METADATA = {}
MODEL_METRICS = {}
DATA_REPORT = {}

if MODEL_PATH.exists():
    MODEL = joblib.load(MODEL_PATH)
if METADATA_PATH.exists():
    MODEL_METADATA = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
if METRICS_PATH.exists():
    MODEL_METRICS = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
if DATA_REPORT_PATH.exists():
    DATA_REPORT = json.loads(DATA_REPORT_PATH.read_text(encoding="utf-8"))


app = FastAPI(
    title="PropertyAI Lahore API",
    version="0.2"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PropertyInput(BaseModel):

    location: str = Field(
        min_length=1,
        max_length=200
    )

    area_sqft: float = Field(
        gt=100,
        le=100000
    )

    bedrooms: int = Field(
        ge=0,
        le=20
    )

    bathrooms: int = Field(
        ge=0,
        le=20
    )

    latitude: float | None = None

    longitude: float | None = None


@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(FRONTEND_PATH / "index.html")


@app.get("/app.js", include_in_schema=False)
def frontend_app():
    return FileResponse(FRONTEND_PATH / "app.js", media_type="text/javascript")


@app.get("/styles.css", include_in_schema=False)
def frontend_styles():
    return FileResponse(FRONTEND_PATH / "styles.css", media_type="text/css")


@app.get("/health")
def health():

    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "model_path": str(MODEL_PATH)
    }


@app.get("/metadata")
def metadata():
    """Return the dataset and benchmark facts used by the frontend."""
    selected = MODEL_METADATA.get("selected_model_name")
    selected_result = MODEL_METRICS.get("results", {}).get(selected, {})
    return {
        "status": "ok" if MODEL_METADATA else "metadata_not_ready",
        "dataset": {
            "name": MODEL_METADATA.get("dataset_name"),
            "date": MODEL_METADATA.get("dataset_date"),
            "source": "Open Data Pakistan / Zameen Property Data",
            "geography": "Lahore",
            "property_type": "Residential houses",
            "purpose": "For Sale",
            "processed_rows": DATA_REPORT.get("final_row_count"),
        },
        "model": {
            "name": selected,
            "type": MODEL_METADATA.get("model_type"),
            "test_rows": MODEL_METADATA.get("test_rows"),
            "test_mae_pkr": selected_result.get("mae_pkr"),
            "r2": selected_result.get("r2"),
            "prediction_interval_status": MODEL_METADATA.get(
                "prediction_interval_status", "not_calibrated"
            ),
        },
        "warning": MODEL_METADATA.get("historical_data_warning"),
        "limitations": MODEL_METADATA.get("limitations", []),
    }


@app.post("/predict")
def predict(p: PropertyInput):

    if MODEL is None:

        return {
            "status": "model_not_ready",
            "message": "The Lahore valuation model has not been trained yet.",
            "next_step": "Collect and prepare the real Lahore property dataset."
        }

    row = pd.DataFrame([
        p.model_dump()
    ])

    pred = float(
        np.expm1(
            MODEL.predict(row)[0]
        )
    )

    return {

        "estimated_price_pkr": round(pred),

        "low_pkr": None,

        "high_pkr": None,

        "currency": "PKR",

        "prediction_interval_status": MODEL_METADATA.get(
            "prediction_interval_status", "not_calibrated"
        ),

        "held_out_error_statistics": MODEL_METADATA.get(
            "held_out_error_statistics", {}
        ),

        "note": (
            "Model estimate based on historical listing data; "
            "asking price is not a verified transaction price. "
            "A prediction interval has not been calibrated."
        )
    }


def run_server():
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )


if __name__ == "__main__":
    run_server()