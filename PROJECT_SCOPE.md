# PROJECT SCOPE — PropertyAI Lahore

> **Authority.** This is the highest-authority document in this repository.
> If any other document, task, or change request conflicts with this file,
> PROJECT_SCOPE.md wins. Do not silently rewrite it. Follow the Scope Change Rule at the end.

## 1. Project

**PropertyAI Lahore** — a Lahore-focused real-estate analytics and valuation platform.

The repository currently contains an early scaffold (a FastAPI `/health` and `/predict`
endpoint, a historical-data training script, reference data and a static frontend page).
That scaffold exists to prove the pipeline end-to-end. It is **not** the finished product,
and it does **not** change the scope defined here.

## 2. Core Purpose

Build a Lahore-focused real-estate analytics and valuation platform using real, traceable
property data.

The platform should eventually estimate **current asking-price ranges** for properties and
provide supporting comparable-property and market information.

Important distinction:

- The platform estimates **asking-price / market-related values** derived from available
  listing data.
- It must **NOT** claim to know an exact, legally verified **transaction price** unless actual
  transaction data is available.

Every valuation output must be presented as an estimate with a range and a stated data basis,
not as a certified price.

## 3. Geographic Scope

Phase 1 is **Lahore only**.

Do not expand to:

- Islamabad
- Karachi
- Rawalpindi
- Faisalabad
- any other city

unless explicitly approved in a future scope change.

Lahore locality-, society-, phase- and block-level detail **is** in scope, because it is still
Lahore. The data model should be able to represent these levels, but must not be used to onboard
other cities.

## 4. Property Scope

Initial focus:

- **Residential houses.**

Later, and only after explicit approval:

- apartments
- plots
- commercial property

"House" here means an independent, semi-detached or attached residential house.
Sale of bare plots and commercial units is a different modelling problem and is out of Phase 1.

## 5. Transaction Scope

The two markets are separate modelling problems:

- **SALE**
- **RENT**

Never train them as one undifferentiated target. Sale and rent differ in price level, scale,
drivers, seasonality and evaluation metrics. They must have separate datasets, separate models
and separate reporting.

## 6. Core Product Areas

Eventually the product is expected to provide:

1. **Valuation Desk** — estimate an asking-price range for a described property.
2. **Comparable Properties** — similar properties that support the estimate.
3. **Market Intelligence** — locality-level summaries and supporting evidence.
4. **Property Search** — filter and explore listings and reference data.
5. **Locality Analysis** — structure, pricing, coverage and quality per locality.
6. **Market Trends** — how asking prices move over time.
7. **Data Quality / Provenance** — what data exists, where it came from, how fresh it is.

These are delivered in the sequence defined in `PROJECT_ROADMAP.md`. They are not built all at
once, and completing one does not authorise starting the next.

## 7. Data Philosophy

- **Real data first.** No synthetic data presented as real.
- **Historical data stays historical.** It must remain clearly labelled as historical and must
  never be presented as today's market.
- **Current data is dated.** Current/recent data must be identified by collection date and, where
  available, listing date.
- **Provenance is preserved.** Every listing keeps its source, URL (where available), listing id
  (where available) and collection date.
- **Raw data is immutable.** Raw captures are kept separately from processed data.
- **Unknown is not "No".** Missing information is unknown, not a negative answer.

## 8. Model Philosophy

- The model must be evaluated against **real held-out data**.
- Do not optimise for a pretty demo at the expense of validity.
- Do not fabricate model accuracy.
- Do not claim a model is "accurate" without a measured evaluation.
- Prediction ranges must come from a defensible method (for example conformal prediction or
  calibrated residuals), not an arbitrary fixed percentage.
- Current valuation models must use a time-aware validation strategy.
- Sale and rent are modelled separately.

## 9. Non-Goals

Explicitly out of scope:

- a social network
- a property marketplace for user-submitted listings
- a payment platform
- a mortgage platform
- legal property verification
- a government land-registry replacement
- guaranteed property valuation
- a transaction settlement system
- a CRM
- an arbitrary AI chatbot unrelated to the core product
- multi-city expansion during Phase 1
- unnecessary microservices
- unnecessary enterprise infrastructure (Kubernetes, service mesh, etc. are not required)

## 10. Scope Change Rule

Any new major feature must be classified as exactly one of:

- **IN SCOPE** — already covered by this document.
- **FUTURE SCOPE** — valid, but belongs to a later phase. Record it in `PROJECT_ROADMAP.md` or
  `docs/DECISIONS.md`; do not build it now.
- **SCOPE CHANGE REQUIRED** — conflicts with or extends this document. Stop and ask.

No major feature may be silently added.

If a future request conflicts with this document:

1. Identify the conflict.
2. Explain it briefly.
3. Ask whether the scope should be formally changed.

Do not independently expand the project.

## 11. Phase 1 Success Criteria

Phase 1 is successful when the platform can:

- hold traceable, real, dated Lahore house data for sale and for rent;
- produce an asking-price range with an honest, measured error estimate;
- show supporting comparables and data freshness;
- state clearly what it does not know.

Phase 1 is **not** required to be complete, fast or pretty. It is required to be honest and
reproducible.

## 12. Non-Functional Constraints

- **Local-first.** The project must run on a developer machine without cloud services.
- **Low cost.** Free/open tooling is preferred; paid infrastructure requires justification.
- **Reproducible.** Anyone can regenerate processed data and models from raw data plus scripts.
- **Auditable.** Every number shown to a user can be traced to data with a source and a date.
- **Simple.** Prefer fewer moving parts; complexity must be earned by a demonstrated need.

## 13. Key Terms

- **Asking price** — the price a seller advertises; not a verified sale.
- **Transaction price** — an actually completed sale price; not available in listing data.
- **Locality / society / phase / block** — the Lahore place hierarchy used for grouping and
  comparison.
- **Comparable** — a real, similar property used as supporting evidence.
- **Provenance** — the source, identifier and dates attached to a record.
- **Leakage** — future or target-derived information improperly used during evaluation.

