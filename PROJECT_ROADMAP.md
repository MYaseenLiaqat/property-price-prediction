# PROJECT ROADMAP — PropertyAI Lahore

> Companion to `PROJECT_SCOPE.md` (which has final authority). This document defines the
> implementation order. Phases are sequential. Do not start a phase before the previous phase's
> exit criteria are met and reported.

## How to read this roadmap

Each phase lists **Goal**, **Inputs**, **Outputs**, **Entry criteria**, **Exit criteria** and
**Not included**. "Not included" is binding: work in that category belongs to a later phase and
must not be started early.

## PHASE 0 — Project Foundation

- **Goal:** Establish environment, repository structure, API health and governance documents.
- **Inputs:** The current repository scaffold.
- **Outputs:** Working environment, `README`, governance documents, `/health` endpoint.
- **Entry criteria:** Repository exists.
- **Exit criteria:** Environment installs; backend starts; `/health` responds; all governance
  documents exist and are consistent.
- **Not included:** data collection, deduplication, modelling, frontend work.

## PHASE 1 — Data Acquisition

- **Goal:** Investigate sources and acquire recent Lahore listing data with provenance.
- **Inputs:** `data/reference/sources.md`, `docs/data_collection.md`, each source's terms/robots.
- **Outputs:** Immutable raw snapshots (timestamped), each carrying source, URL, listing id where
  available and collection date; a source-access review note.
- **Entry criteria:** Phase 0 complete; target sources and permitted-use status documented.
- **Exit criteria:** At least one compliant, dated, recent Lahore source captured end-to-end and
  stored raw with provenance; access restrictions respected.
- **Not included:** normalization, cleaning, dedup, model training, UI.

## PHASE 2 — Data Engineering

- **Goal:** Normalize raw data into a consistent schema.
- **Inputs:** Raw snapshots from Phase 1.
- **Outputs:** Normalized schema; price normalization (PKR); area normalization
  (Marla/Kanal/sqft and covered area); locality/society/phase/block normalization; documented
  missing-value policy; validation checks.
- **Entry criteria:** Phase 1 raw data available.
- **Exit criteria:** Normalization rules are documented, deterministic, testable and pass
  validation on the acquired data.
- **Not included:** deduplication, dataset construction, EDA, modelling.

## PHASE 3 — Deduplication

- **Goal:** Detect duplicates within and across sources.
- **Inputs:** Normalized listings from Phase 2.
- **Outputs:** Duplicate groups with a `duplicate_group_id`; cross-source matching rules;
  listing-identity policy.
- **Entry criteria:** Phase 2 normalized data available.
- **Exit criteria:** Duplicate logic documented and applied without destroying provenance
  (records are grouped, not silently deleted).
- **Not included:** final dataset construction, modelling.

## PHASE 4 — Dataset Construction

- **Goal:** Build the processed modelling datasets.
- **Inputs:** Deduplicated normalized data.
- **Outputs:** Lahore house datasets split into **sale** and **rent**; a dataset quality report.
- **Entry criteria:** Phase 3 complete.
- **Exit criteria:** Processed datasets exist with documented row counts, coverage and a quality
  report; sale and rent are separate files.
- **Not included:** EDA charts, model training, UI.

## PHASE 5 — EDA

- **Goal:** Understand the data before modelling.
- **Inputs:** Processed datasets.
- **Outputs:** Price distributions, area relationships, locality analysis, price per sqft, price
  per Marla, temporal analysis, outlier analysis.
- **Entry criteria:** Phase 4 datasets exist.
- **Exit criteria:** Findings documented; outliers classified (luxury, data-entry error, unit
  error, duplicate, unusual type) rather than blindly removed.
- **Not included:** model training, API changes, UI.

## PHASE 6 — ML Benchmarking

- **Goal:** Benchmark candidate models honestly.
- **Inputs:** Processed datasets and EDA findings.
- **Outputs:** Baseline model; tree-based models; gradient-boosting models; categorical-feature
  models; time-aware validation; spatial/locality-aware validation where appropriate; a benchmark
  report.
- **Entry criteria:** Phase 5 complete.
- **Exit criteria:** Models compared on real held-out data with MAE/RMSE/median-AE/R² reported;
  a best candidate selected with evidence; leakage checks passed.
- **Not included:** production API wiring, UI, comparables, market intelligence.

## PHASE 7 — Valuation Engine

- **Goal:** Turn the chosen model into an honest valuation engine.
- **Inputs:** Benchmark winner; processed datasets; validation strategy.
- **Outputs:** Point estimate; prediction range from a defensible method; confidence / data-quality
  information; current-market adjustment only where methodologically justified.
- **Entry criteria:** Phase 6 complete.
- **Exit criteria:** Engine returns a range plus a data-quality/confidence signal; the range method
  is documented; unit tests pass.
- **Not included:** comparables UI, market dashboards, deployment.

## PHASE 8 — Comparable Properties

- **Goal:** Find and present comparable properties supporting an estimate.
- **Inputs:** Valuation engine outputs; processed datasets.
- **Outputs:** Similarity search; locality-aware comparisons; supporting market evidence.
- **Entry criteria:** Phase 7 complete.
- **Exit criteria:** Comparables are retrieved from real data, locality-aware, and clearly
  separated from model output.
- **Not included:** maps, full search UI, market dashboards.

## PHASE 9 — Market Intelligence

- **Goal:** Provide locality and market-level analysis.
- **Inputs:** Processed datasets; reference/index data; valuation engine.
- **Outputs:** Locality trends; price trends; supply/listing signals **only where data supports
  them**; market dashboards.
- **Entry criteria:** Phase 8 complete.
- **Exit criteria:** Market views are derived from real data with stated coverage, and clearly
  labelled as asking-price-based, not transaction-based.
- **Not included:** production deployment, automated refresh.

## PHASE 10 — Frontend

- **Goal:** Deliver a professional real-estate interface.
- **Inputs:** API endpoints from Phases 7–9; `DESIGN_GUIDELINES.md`.
- **Outputs:** Valuation workflow; comparables view; market intelligence views; property search;
  maps where appropriate.
- **Entry criteria:** Backend endpoints stable and documented.
- **Exit criteria:** The full valuation workflow works end-to-end against the real API.
- **Not included:** new modelling work, new data sources.

## PHASE 11 — Production

- **Goal:** Operate the platform reliably.
- **Inputs:** Working system from Phases 0–10.
- **Outputs:** Automated data refresh; monitoring; model versioning; deployment; reliability
  practices.
- **Entry criteria:** Phase 10 complete; refresh, monitoring and versioning designed.
- **Exit criteria:** Scheduled refresh, monitoring, model versioning and a deployment path exist
  and are documented.
- **Not included:** new product features; scope expansion.

## Sequencing rule

Do not add additional major phases. Do not merge phases. Complete one phase, report, and stop.

