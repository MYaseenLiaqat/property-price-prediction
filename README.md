# PropertyAI Lahore

A Lahore-first property valuation platform designed around real-world user inputs.

## Read this first

**Read `PROJECT_SCOPE.md` before making project changes.**

Supporting governance documents: `PROJECT_ROADMAP.md`, `ARCHITECTURE.md`,
`DEVELOPMENT_RULES.md`, `DATA_POLICY.md`, `DESIGN_GUIDELINES.md`, `docs/DECISIONS.md`.

## Important data status
This repository does NOT pretend synthetic data is real market data.
The actual training source is the Open Data Pakistan "Zameen Property Data" CSV, which is published with a Creative Commons Attribution license. It is a historical snapshot, not current market truth.

## Run

### 1. Create environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install
```powershell
pip install -r requirements.txt
```

### 3. Download the real historical dataset
```powershell
python scripts/download_open_data.py
```

### 4. Train the Lahore house-sale model
```powershell
python scripts/train_lahore.py
```

This:
- filters Lahore
- filters houses
- filters sale listings
- normalizes area to square feet
- removes impossible values
- removes duplicates when an ID exists
- trims extreme price-per-sqft outliers
- compares Random Forest and Extra Trees
- saves the best model to `models/lahore_house_sale_model.joblib`
- writes metrics to `models/metrics.json`

### 5. Start API
```powershell
uvicorn backend.main:app --reload
```

### 6. Open frontend
Open `frontend/index.html`.

## Production roadmap
1. Add current, compliant marketplace collection.
2. Keep raw snapshots immutable and timestamped.
3. Deduplicate cross-source listings.
4. Add rent model separately.
5. Add conformal prediction intervals instead of the temporary ±16% UI interval.
6. Add location/geospatial features.
7. Add comparable-property retrieval.
8. Add time-based validation to prevent temporal leakage.
9. Add monitoring for drift and stale inventory.
10. Deploy API + database + frontend.

## Data sources
See `data/reference/sources.md`.
