# ARCHITECTURE — PropertyAI Lahore

> Companion to `PROJECT_SCOPE.md` (final authority) and `PROJECT_ROADMAP.md`. This document
> describes the **target** architecture. It is a design, not an implementation task. Do not build
> components described here until their phase begins.

## Guiding principles

- **Modular but simple.** Clear layers, small interfaces, no premature complexity.
- **Monolith first.** One FastAPI backend service. No microservices unless a demonstrated need
  appears and is explicitly approved.
- **No Kubernetes, no cloud requirement.** Early development runs locally.
- **Raw data is immutable.** Processed data is reproducible from raw data.
- **Provenance travels with data.**
- **Honest outputs.** Every valuation carries a range and a data-quality signal.

## Target data flow

```
DATA SOURCES
    |
    v
DATA ACQUISITION
    |
    v
RAW DATA
    |
    v
NORMALIZATION
    |
    v
VALIDATION
    |
    v
DEDUPLICATION
    |
    v
PROCESSED DATA
    |
    v
EDA / DATA QUALITY
    |
    v
MODEL TRAINING
    |
    v
MODEL EVALUATION
    |
    v
VALUATION ENGINE
    |
    v
FASTAPI
    |
    v
FRONTEND
```

## Layers

### DATA LAYER

- **Raw listings** — immutable, timestamped captures, one file/folder per source and collection
  date. Never edited in place.
- **Processed listings** — normalized, validated, deduplicated listings, separated into sale and
  rent. Reproducible from raw.
- **Reference / index data** — market indices and benchmark snapshots used for context, kept
  separate from listing-level training data to avoid leakage.
- **Locality dictionaries** — controlled vocabularies for locality, society, phase, block and
  their aliases, so the same place is spelled the same way everywhere.
- **Provenance** — source, URL, listing id, collection date and listing date stored per record.

### ML LAYER

- **Feature engineering** — deterministic transforms from processed listings to model features.
- **Training** — separate pipelines for sale and rent.
- **Evaluation** — measured on real held-out data with time-aware and locality-aware splits.
- **Model artifacts** — serialized models stored with their metadata.
- **Versioning** — every artifact records training data range, feature set, metrics and code
  version.

### API LAYER (FastAPI, monolith)

- `/health` — service and model readiness.
- **Valuation** — given property attributes, return an asking-price range, a point estimate, a
  confidence/data-quality signal and a comparable count.
- **Comparables** — retrieve nearby/similar properties from real data.
- **Market information** — locality-level summaries and trends with stated coverage.

### FRONTEND

- Valuation desk, property profile, comparables, market intelligence and search views.
- Built after the data and model foundation (Phase 10). No framework is chosen yet.

## Repository layout (target)

```
backend/        API layer (FastAPI)
frontend/       UI (Phase 10)
data/
  raw/          immutable captures (Phase 1)
  processed/    normalized datasets (Phases 2-4)
  reference/    indices and dictionaries
docs/           phase docs and DECISIONS.md
scripts/        acquisition, ETL and training entry points
models/         versioned model artifacts and metrics
```

## Boundaries and rules

- The API reads processed data and model artifacts; it does not clean raw data at request time.
- Reference/index data must never be used as a training target.
- The frontend talks only to the API; it must not duplicate valuation logic.
- Data processing is scripted and reproducible, not manual.

## Component responsibilities

| Component | Responsibility | Must not do |
| --- | --- | --- |
| Acquisition | Capture raw listings with provenance | Clean or interpret data |
| Normalization | Map raw fields to a common schema | Drop provenance |
| Validation | Flag impossible values | Silently delete rows |
| Deduplication | Group duplicate listings | Delete provenance |
| EDA | Describe the data and its quality | Feed the model directly |
| Training / Evaluation | Fit and score models on held-out data | See the test period |
| Valuation engine | Produce ranges plus confidence | Claim exact prices |
| API | Serve data and model output | Clean data at request time |
| Frontend | Present results with evidence | Recompute valuations |

## Cross-cutting concerns

- **Provenance** — attached to every record and carried through each layer.
- **Reproducibility** — every artifact is rebuildable from raw data plus scripts.
- **Versioning** — datasets, features and models each carry a version identifier.
- **Observability** — health checks plus data/model freshness reporting are part of the API.

## Data contracts (sketch)

- Processed listings expose at least: `source`, `listing_id`, `listing_url`, `date_collected`,
  `date_listed`, `purpose` (sale/rent), `city`, `locality`, `price_pkr`, `area_sqft`, `bedrooms`,
  `bathrooms`.
- The valuation endpoint returns: a point estimate, a range, a data-quality/confidence signal, a
  comparable count, and a caveat that the value is an asking-price estimate.

## Deliberate non-decisions

- No database is introduced yet. Files are sufficient until volume requires otherwise, and adding
  a database requires explicit approval.
- No authentication, payments or multi-tenancy.
- No microservices, message queues or orchestration platforms.

## When to revisit this architecture

Revisit only when data volume outgrows files, request load requires a database/cache, or the scope
changes. Any such change goes through the Scope Change Rule in `PROJECT_SCOPE.md`.
