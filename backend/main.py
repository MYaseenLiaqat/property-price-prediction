from pathlib import Path

import joblib
import pandas as pd
import numpy as np

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE / "models" / "lahore_house_sale_model.joblib"

MODEL = None

if MODEL_PATH.exists():
    MODEL = joblib.load(MODEL_PATH)


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


@app.get("/health")
def health():

    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "model_path": str(MODEL_PATH)
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

    low = pred * 0.84
    high = pred * 1.16

    return {

        "estimated_price_pkr": round(pred),

        "low_pkr": round(low),

        "high_pkr": round(high),

        "currency": "PKR",

        "note": (
            "Model estimate based on historical listing data; "
            "asking price is not a verified transaction price."
        )
    }