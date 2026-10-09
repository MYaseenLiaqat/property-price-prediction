"""Prepare the historical Lahore house-sale modelling dataset.

This script only transforms the downloaded source CSV. It does not create data.
The source is a historical asking-price snapshot and is not current market data.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw" / "zameen_property_data.csv"
PROCESSED = BASE / "data" / "processed" / "lahore_house_sale.csv"
SOURCE_REPORT = BASE / "data" / "reference" / "historical_lahore_data_report.json"
DATA_REPORT = BASE / "data" / "reference" / "lahore_house_sale_data_report.json"
SOURCE_URL = (
    "https://opendata.com.pk/dataset/property-data-for-pakistan/resource/"
    "2cb1eeea-8dff-41b4-845f-28b8d75ca23b"
)
DATASET_DATE = "2020-05-15"
MARLA_SQFT = 272.25
KANAL_SQFT = 5445.0


def _json_value(value: object) -> object:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _stats(series: pd.Series) -> dict[str, object]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return {"count": 0}
    return {
        "count": int(numeric.size),
        "min": _json_value(numeric.min()),
        "max": _json_value(numeric.max()),
        "mean": _json_value(numeric.mean()),
        "median": _json_value(numeric.median()),
        "q1": _json_value(numeric.quantile(0.25)),
        "q3": _json_value(numeric.quantile(0.75)),
    }


def _parse_area(value: object) -> tuple[float, str]:
    text = str(value).strip().casefold()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return np.nan, "unknown"
    amount = float(match.group(1))
    if "kanal" in text:
        return amount * KANAL_SQFT, "kanal"
    if "marla" in text:
        return amount * MARLA_SQFT, "marla"
    if "sq" in text or "feet" in text or "ft" in text:
        return amount, "sqft"
    return np.nan, "unknown"


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Source data not found: {RAW}. Run scripts/download_open_data.py first.")

    collected_at = date.today().isoformat()
    raw = pd.read_csv(RAW, low_memory=False)
    expected_columns = list(raw.columns)
    source_missingness = {
        str(key): int(value) for key, value in raw.isna().sum().items()
    }

    city_counts = {str(k): int(v) for k, v in raw["city"].value_counts().items()}
    lahore = raw[raw["city"].astype("string").str.casefold().eq("lahore")].copy()
    house = lahore[
        lahore["property_type"].astype("string").str.casefold().eq("house")
    ].copy()
    sale = house[
        house["purpose"].astype("string").str.casefold().eq("for sale")
    ].copy()

    source_report = {
        "dataset_name": "Zameen Property Data.csv",
        "source_organization": "Open Data Pakistan",
        "source_url": SOURCE_URL,
        "license": "Creative Commons Attribution (publisher-stated)",
        "dataset_date": DATASET_DATE,
        "download_or_inspection_date": collected_at,
        "source_file": str(RAW.relative_to(BASE)),
        "total_rows": int(len(raw)),
        "total_columns": int(len(raw.columns)),
        "exact_column_names": expected_columns,
        "city_counts": city_counts,
        "lahore_row_count": int(len(lahore)),
        "lahore_property_type_counts": {
            str(k): int(v) for k, v in lahore["property_type"].value_counts().items()
        },
        "lahore_purpose_counts": {
            str(k): int(v) for k, v in lahore["purpose"].value_counts().items()
        },
        "lahore_house_sale_row_count": int(len(sale)),
        "lahore_house_rent_row_count": int(
            len(
                lahore[
                    lahore["property_type"].astype("string").str.casefold().eq("house")
                    & lahore["purpose"].astype("string").str.casefold().eq("for rent")
                ]
            )
        ),
        "field_inventory": {
            "price": "price",
            "area": "area",
            "bedrooms": "bedrooms",
            "bathrooms": "baths",
            "location": "location",
            "latitude": "latitude",
            "longitude": "longitude",
            "listing_date": "date_added",
            "listing_url": "page_url",
            "listing_id": "property_id",
        },
        "missing_values": source_missingness,
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "lahore_exact_duplicate_rows": int(lahore.duplicated().sum()),
        "lahore_duplicate_property_ids": int(lahore["property_id"].duplicated().sum()),
        "lahore_duplicate_urls": int(lahore["page_url"].duplicated().sum()),
        "observed_price_statistics_lahore_house_sale": _stats(sale["price"]),
        "observed_area_values_lahore_house_sale": {
            str(k): int(v) for k, v in sale["area"].value_counts().head(20).items()
        },
        "observed_bedroom_values_lahore_house_sale": {
            str(k): int(v) for k, v in sale["bedrooms"].value_counts().items()
        },
        "observed_bathroom_values_lahore_house_sale": {
            str(k): int(v) for k, v in sale["baths"].value_counts().items()
        },
        "observed_extreme_values": {
            "price_zero_or_negative": int((sale["price"] <= 0).sum()),
            "price_below_100000": int((sale["price"] < 100000).sum()),
            "maximum_price": _json_value(sale["price"].max()),
            "maximum_bedrooms": _json_value(sale["bedrooms"].max()),
            "maximum_bathrooms": _json_value(sale["baths"].max()),
        },
        "limitations": [
            "Historical marketplace listing snapshot, not current 2026 data.",
            "Prices are asking prices, not verified transaction prices.",
            "The source has no reliable collection-date series for current temporal validation.",
            "The downloaded Lahore subset contains no house-rent rows.",
            "Agency and agent fields are not used and may contain personal or unnecessary data.",
        ],
    }

    working = sale.copy()
    working["area_sqft"], working["area_unit"] = zip(
        *working["area"].map(_parse_area)
    )
    for column in ["price", "bedrooms", "baths", "latitude", "longitude"]:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    before_filters = len(working)
    valid = (
        working["price"].gt(0)
        & working["area_sqft"].gt(0)
        & working["bedrooms"].ge(0)
        & working["baths"].ge(0)
        & working["latitude"].between(-90, 90)
        & working["longitude"].between(-180, 180)
        & working["location"].notna()
    )
    invalid_value_rows = int((~valid).sum())
    working = working.loc[valid].copy()

    # Very low positive prices are retained for auditability but excluded as
    # clearly suspicious asking-price records from the modelling table.
    suspicious_price_rows = int(working["price"].lt(100000).sum())
    working = working.loc[working["price"].ge(100000)].copy()

    exact_duplicates = int(working.duplicated().sum())
    working = working.drop_duplicates().copy()

    output = pd.DataFrame(
        {
            "source": "Open Data Pakistan / Zameen Property Data",
            "source_url": SOURCE_URL,
            "dataset_date": DATASET_DATE,
            "property_id": working["property_id"],
            "location_id": working["location_id"],
            "listing_url": working["page_url"],
            "date_added": working["date_added"],
            "purpose": "sale",
            "property_type": "house",
            "city": working["city"].astype("string").str.strip(),
            "province_name": working["province_name"].astype("string").str.strip(),
            "location": working["location"].astype("string").str.strip(),
            "price_pkr": working["price"],
            "area_raw": working["area"].astype("string").str.strip(),
            "area_unit": working["area_unit"],
            "area_sqft": working["area_sqft"],
            "bedrooms": working["bedrooms"],
            "bathrooms": working["baths"],
            "latitude": working["latitude"],
            "longitude": working["longitude"],
        }
    )
    output = output.sort_values("property_id").reset_index(drop=True)
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(PROCESSED, index=False)

    missingness = {
        str(key): int(value) for key, value in output.isna().sum().items()
    }
    price_per_sqft = output["price_pkr"] / output["area_sqft"]
    data_report = {
        "dataset_name": "lahore_house_sale.csv",
        "source_dataset": "Zameen Property Data.csv",
        "source_dataset_date": DATASET_DATE,
        "prepared_at": collected_at,
        "source_row_count": int(len(raw)),
        "lahore_row_count": int(len(lahore)),
        "house_row_count": int(len(house)),
        "sale_row_count": int(len(sale)),
        "final_row_count": int(len(output)),
        "rows_removed": int(before_filters - len(output)),
        "invalid_value_rows_removed": invalid_value_rows,
        "suspicious_low_price_rows_removed": suspicious_price_rows,
        "exact_duplicate_count_removed": exact_duplicates,
        "missingness": missingness,
        "price_statistics_pkr": _stats(output["price_pkr"]),
        "area_statistics_sqft": _stats(output["area_sqft"]),
        "price_per_sqft_statistics": _stats(price_per_sqft),
        "location_statistics": {
            "unique_locations": int(output["location"].nunique()),
            "top_locations": {
                str(k): int(v) for k, v in output["location"].value_counts().head(20).items()
            },
            "latitude_statistics": _stats(output["latitude"]),
            "longitude_statistics": _stats(output["longitude"]),
        },
        "filtering_rules": [
            "Select city case-insensitively equal to Lahore.",
            "Select property_type case-insensitively equal to House.",
            "Select purpose case-insensitively equal to For Sale.",
            "Parse Marla as 272.25 square feet and Kanal as 5,445 square feet.",
            "Remove rows with non-positive price or area, invalid coordinates, negative beds/baths, or missing location.",
            "Exclude positive prices below PKR 100,000 as suspicious records; the count is reported.",
            "Remove exact duplicate rows after normalization.",
            "No missing bedroom, bathroom, location, coordinate, price, or area values were fabricated.",
            "No utility fields exist in the source; missing utility information remains unavailable, not No.",
        ],
        "outlier_investigation": {
            "low_price_threshold_pkr": 100000,
            "low_price_rows_excluded": suspicious_price_rows,
            "price_min_after_filter": _json_value(output["price_pkr"].min()),
            "price_max_after_filter": _json_value(output["price_pkr"].max()),
            "area_min_after_filter_sqft": _json_value(output["area_sqft"].min()),
            "area_max_after_filter_sqft": _json_value(output["area_sqft"].max()),
            "price_per_sqft_min": _json_value(price_per_sqft.min()),
            "price_per_sqft_max": _json_value(price_per_sqft.max()),
            "note": "Extreme valid values are retained; only impossible or explicitly suspicious records are filtered.",
        },
        "limitations": [
            "Historical snapshot from 2020 with listings dated in 2019; not current 2026 market data.",
            "No reliable temporal holdout for current-market validation.",
            "Asking prices are not verified transaction prices.",
            "This snapshot contains Lahore house-sale listings but no Lahore house-rent rows.",
            "Source has no utility attributes, so utility effects cannot be modelled.",
        ],
    }

    SOURCE_REPORT.write_text(json.dumps(source_report, indent=2, default=_json_value), encoding="utf-8")
    DATA_REPORT.write_text(json.dumps(data_report, indent=2, default=_json_value), encoding="utf-8")
    print(json.dumps({
        "source_rows": len(raw),
        "lahore_rows": len(lahore),
        "house_sale_rows": len(sale),
        "final_rows": len(output),
        "processed": str(PROCESSED),
        "source_report": str(SOURCE_REPORT),
        "data_report": str(DATA_REPORT),
    }, indent=2))


if __name__ == "__main__":
    main()
