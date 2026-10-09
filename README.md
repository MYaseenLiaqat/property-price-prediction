# EstateIQ / PropertyAI Lahore

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

### 5. Provision the model artifact

The 232 MB model is intentionally not stored in ordinary Git. A clean environment
must receive it from a release or object-storage URL and verify its SHA-256 checksum:

```powershell
$env:MODEL_ARTIFACT_URL = "https://example.invalid/releases/download/v0.1.0/lahore_house_sale_model.joblib"
$env:MODEL_ARTIFACT_SHA256 = "5609684d524a68bcf3bca0e653db1c85bf2fb874ccf6391de85babce8eacb910"
python scripts/provision_model.py
```

The URL above is a placeholder and must be replaced with the URL of an authorized
release asset. The checksum is recorded in
`models/model_artifact_manifest.json`. The provisioner downloads to a temporary file,
checks the complete SHA-256 digest, and atomically installs the artifact only after
verification.

### 6. Start API and frontend

FastAPI serves the frontend and API from one origin:

```powershell
python -m backend.main
```

The launcher binds to `0.0.0.0` and reads `PORT`, defaulting to `8000`:

```powershell
$env:PORT = "8000"
python -m backend.main
```

Open `http://127.0.0.1:8000/`. For the separate local frontend server on port
5500, the frontend retains its explicit `http://127.0.0.1:8000` development
override; production same-origin requests remain relative.

## Deployment readiness

The included `render.yaml` prepares a free Render web service without deploying it.
Its build installs the pinned runtime dependencies, its start command verifies the
model artifact before starting FastAPI, and `/health` is configured as the health
check. Set `MODEL_ARTIFACT_URL` to an authorized GitHub Release asset (or another
lawful HTTPS artifact host) and set `MODEL_ARTIFACT_SHA256` to the recorded digest.
Do not use the unverified Zameen index snapshot.

Render's free web service is suitable for a low-volume demonstration, not guaranteed
production availability: it may sleep after inactivity, has ephemeral local
storage, and rebuilds/redeploys must provision the model again. The model is
downloaded at startup rather than committed to Git. A release asset or external
artifact host must remain accessible and within the host's request/build limits.
No billing or deployment has been configured by this project.

Before deployment, publish the model as a release asset and verify the downloaded
file with:

```powershell
Get-FileHash models/lahore_house_sale_model.joblib -Algorithm SHA256
```

The output must match
`5609684d524a68bcf3bca0e653db1c85bf2fb874ccf6391de85babce8eacb910`.

Run the focused integration tests with:

```powershell
python -m unittest discover -s tests -v
```

## Production roadmap
1. Add current, compliant marketplace collection.
2. Keep raw snapshots immutable and timestamped.
3. Deduplicate cross-source listings.
4. Add rent model separately.
5. Add calibrated prediction intervals; the current API explicitly reports that intervals are
   not calibrated.
6. Add location/geospatial features.
7. Add comparable-property retrieval.
8. Add time-based validation to prevent temporal leakage.
9. Add monitoring for drift and stale inventory.
10. Deploy API + database + frontend.

## Data sources
See `data/reference/sources.md`.
