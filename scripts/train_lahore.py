from pathlib import Path
import re, json, warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore")
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw" / "zameen_property_data.csv"
PROC = BASE / "data" / "processed" / "lahore_houses_clean.csv"
MODEL_DIR = BASE / "models"
MODEL_DIR.mkdir(exist_ok=True)
PROC.parent.mkdir(parents=True, exist_ok=True)

if not RAW.exists():
    raise SystemExit("Real dataset not found. Run: python scripts/download_open_data.py")

df = pd.read_csv(RAW, low_memory=False)
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

def pick(*names):
    for n in names:
        if n in df.columns:
            return n
    return None

price_col = pick("price", "price_pkr")
city_col = pick("city")
ptype_col = pick("property_type", "propertytype")
purpose_col = pick("purpose")
location_col = pick("location", "area")
beds_col = pick("bedrooms", "beds")
baths_col = pick("bath", "baths", "bathrooms")
area_col = pick("area", "area_size")
area_type_col = pick("area_type", "area_unit")
lat_col = pick("latitude", "lat")
lon_col = pick("longitude", "lng", "lon")

required = [price_col, city_col, ptype_col, purpose_col, location_col, area_col]
if any(x is None for x in required):
    raise SystemExit(f"Could not map required columns. Found: {list(df.columns)}")

# Lahore + house + sale only. Purpose/property type matching is deliberately broad.
x = df.copy()
x[city_col] = x[city_col].astype(str).str.strip()
x[ptype_col] = x[ptype_col].astype(str).str.lower()
x[purpose_col] = x[purpose_col].astype(str).str.lower()

x = x[x[city_col].str.lower().eq("lahore")]
x = x[x[ptype_col].str.contains("house", na=False)]
x = x[x[purpose_col].str.contains("sale|sell|buy", na=False)]

# Numeric conversion
for c in [price_col, beds_col, baths_col, area_col, lat_col, lon_col]:
    if c:
        x[c] = pd.to_numeric(x[c], errors="coerce")

# Area normalization. The old dataset can encode area in marla/kanal/sqft.
unit = x[area_type_col].astype(str).str.lower() if area_type_col else pd.Series("", index=x.index)
area = pd.to_numeric(x[area_col], errors="coerce")

def area_to_sqft(a, u):
    u = str(u).lower()
    if "kanal" in u:
        return a * 5445
    if "marla" in u:
        return a * 272.25
    if "sq" in u or "feet" in u or "ft" in u:
        return a
    # Many versions of the dataset use Area Size like "5 Marla" in a text column.
    return a

x["area_sqft"] = [area_to_sqft(a, u) for a, u in zip(area, unit)]
x["area_sqft"] = pd.to_numeric(x["area_sqft"], errors="coerce")

# If the area column contains strings such as "10 Marla", recover the number/unit.
if x["area_sqft"].isna().mean() > 0.2:
    raw_area = df.loc[x.index, area_col].astype(str)
    nums = pd.to_numeric(raw_area.str.extract(r"([0-9]+(?:\.[0-9]+)?)")[0], errors="coerce")
    units = raw_area.str.lower()
    x.loc[nums.notna(), "area_sqft"] = [
        area_to_sqft(a, u) for a, u in zip(nums[nums.notna()], units[nums.notna()])
    ]

x["price_pkr"] = pd.to_numeric(x[price_col], errors="coerce")
x["bedrooms_clean"] = pd.to_numeric(x[beds_col], errors="coerce") if beds_col else np.nan
x["bathrooms_clean"] = pd.to_numeric(x[baths_col], errors="coerce") if baths_col else np.nan
x["location_clean"] = x[location_col].astype(str).str.strip()

# Drop impossible values and duplicates.
x = x[(x["price_pkr"] > 0) & (x["area_sqft"] > 0)]
x = x[(x["area_sqft"] >= 200) & (x["area_sqft"] <= 100000)]
x = x[(x["price_pkr"] >= 300000) & (x["price_pkr"] <= 2_000_000_000)]

id_col = pick("property_id", "propertyid", "id")
if id_col:
    x = x.drop_duplicates(subset=[id_col])
else:
    x = x.drop_duplicates(subset=["location_clean","price_pkr","area_sqft","bedrooms_clean","bathrooms_clean"])

# Remove extreme price/area combinations using robust price-per-sqft bounds.
x["price_per_sqft"] = x["price_pkr"] / x["area_sqft"]
lo, hi = x["price_per_sqft"].quantile([0.01, 0.99])
x = x[x["price_per_sqft"].between(lo, hi)]

features = pd.DataFrame({
    "location": x["location_clean"],
    "area_sqft": x["area_sqft"],
    "bedrooms": x["bedrooms_clean"],
    "bathrooms": x["bathrooms_clean"],
})
if lat_col: features["latitude"] = x[lat_col]
if lon_col: features["longitude"] = x[lon_col]

y = np.log1p(x["price_pkr"].astype(float))

cat = ["location"]
num = [c for c in features.columns if c not in cat]

pre = ColumnTransformer([
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), cat),
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ]), num)
])

Xtr, Xte, ytr, yte = train_test_split(features, y, test_size=0.2, random_state=42)

models = {
    "random_forest": RandomForestRegressor(
        n_estimators=350, max_depth=28, min_samples_leaf=2, n_jobs=-1, random_state=42
    ),
    "extra_trees": ExtraTreesRegressor(
        n_estimators=350, max_depth=32, min_samples_leaf=2, n_jobs=-1, random_state=42
    ),
}

results = {}
trained = {}
for name, reg in models.items():
    pipe = Pipeline([("preprocess", pre), ("model", reg)])
    pipe.fit(Xtr, ytr)
    pred = np.expm1(pipe.predict(Xte))
    actual = np.expm1(yte)
    results[name] = {
        "mae_pkr": float(mean_absolute_error(actual, pred)),
        "rmse_pkr": float(mean_squared_error(actual, pred) ** 0.5),
        "median_absolute_error_pkr": float(median_absolute_error(actual, pred)),
        "r2": float(r2_score(actual, pred)),
        "rows": int(len(x))
    }
    trained[name] = pipe

best = min(results, key=lambda k: results[k]["mae_pkr"])
joblib.dump(trained[best], MODEL_DIR / "lahore_house_sale_model.joblib")

x.to_csv(PROC, index=False)
(MODEL_DIR / "metrics.json").write_text(json.dumps({
    "best_model": best,
    "results": results,
    "dataset_rows_after_cleaning": int(len(x)),
    "source": "Open Data Pakistan / Zameen Property Data",
    "note": "Historical listing data; not current market truth."
}, indent=2), encoding="utf-8")

print(json.dumps({
    "best_model": best,
    "results": results,
    "clean_rows": len(x),
    "processed": str(PROC),
}, indent=2))
