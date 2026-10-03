# DECISIONS — Architecture Decision Log

Lightweight ADR-style log for PropertyAI Lahore. New decisions are appended; existing decisions
are not silently rewritten — supersede them with a new entry instead.

| Field | Meaning |
| --- | --- |
| Status | Accepted / Superseded / Proposed |
| Date | Date recorded (YYYY-MM-DD) |
| Decision | What was decided |
| Reason | Why |
| Consequences | What it implies for future work |

---

## Decision 001 — Lahore is the initial geographic scope

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Phase 1 covers Lahore only.
- **Reason:** A Lahore focus keeps the data, locality vocabulary and market behaviour consistent
  and makes honest evaluation possible before scaling.
- **Consequences:** No other city is onboarded without a formal scope change. Locality, society,
  phase and block detail remain in scope.

## Decision 002 — Real listing data is required for the serious valuation model

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** The production valuation model must be built on real, traceable listing data.
- **Reason:** Synthetic or untraceable data cannot support honest accuracy claims.
- **Consequences:** Data acquisition and validation come before modelling. No fabricated data may
  be treated as real market data.

## Decision 003 — 2020 historical data must not be presented as current 2026 market data

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Historical snapshots (e.g. Open Data Pakistan / Zameen) are labelled historical
  and never shown as today's market.
- **Reason:** Presenting old prices as current would mislead users and invalidate the product.
- **Consequences:** Current outputs require recent, dated listings or an explicit temporal
  adjustment method.

## Decision 004 — Sale and rent are separate modelling problems

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Sale and rent are modelled, stored and evaluated separately.
- **Reason:** They differ in scale, drivers and metrics; a single target would blur both.
- **Consequences:** Separate datasets, models, metrics and reporting.

## Decision 005 — Raw data must be preserved separately from processed data

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Raw captures are immutable; processed data is derived and reproducible.
- **Reason:** Reversibility and auditability; allows re-cleaning without re-collecting.
- **Consequences:** Raw and processed live in separate locations; processing is scripted.

## Decision 006 — Listing provenance must be preserved

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Every listing keeps source, listing id/url where available, collection date and
  listing date where available.
- **Reason:** Trust, deduplication, freshness reporting and legal hygiene depend on provenance.
- **Consequences:** No transform may drop provenance fields.

## Decision 007 — Missing utility information is Unknown, not automatically No

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Missing attributes remain unknown; they are not converted to a negative value.
- **Reason:** "Unknown" and "No" are different facts; conflating them biases the model and
  misleads users.
- **Consequences:** Missing-value handling is explicit and documented.

## Decision 008 — Time-aware validation will be used for current valuation modelling

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Current valuation models use time-aware validation and leakage checks.
- **Reason:** Random splits leak future information and overstate accuracy in a drifting market.
- **Consequences:** Splits are based on time where dates exist; leakage review is a quality gate.

## Decision 009 — Marketplace asking prices must not be described as verified transaction prices

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Outputs describe estimated asking-price ranges, never verified sale prices.
- **Reason:** Listing prices are asking prices and are not verified transactions.
- **Consequences:** UI copy, API responses and docs must use asking-price language and caveats.

## Decision 010 — Frontend development comes after the data/model foundation

- **Status:** Accepted
- **Date:** 2026-10-03
- **Decision:** Frontend work starts at Phase 10, after data, validation and modelling.
- **Reason:** A polished UI over an invalid model would be misleading and expensive to redo.
- **Consequences:** No CSS/JS/frontend-framework work before Phase 10; `DESIGN_GUIDELINES.md`
  captures the direction in the meantime.

