# DATA POLICY — PropertyAI Lahore

> Defines the project's data-integrity rules. Companion to `PROJECT_SCOPE.md` (final authority).
> These rules are binding for anyone collecting, transforming or modelling data in this
> repository.

## Data categories

Keep these categories distinct at all times:

1. **Raw listing data** — unmodified captures from a source, with a collection timestamp.
   Immutable. Never edited, cleaned or "fixed" in place.
2. **Processed listing data** — normalized/validated/deduplicated listings derived from raw data.
   Reproducible; must trace back to raw.
3. **Historical market data** — older snapshots (for example the Open Data Pakistan / Zameen
   CSV). Useful as a baseline; **never** presented as the current market.
4. **Current/recent listing data** — recent marketplace listings, dated by collection and, where
   available, listing date.
5. **Market index / reference data** — area-level benchmarks and trend snapshots. Context only;
   must not be used as a training target.
6. **Model-derived data** — predictions, ranges, comparables and derived features. Clearly
   derived, never presented as observed market facts.

Do not mix categories in one file without a column that identifies the category and its date.

## Provenance

Each listing should preserve:

- `source`
- `listing_id` where available
- `listing_url` where available
- `date_collected`
- `date_listed` where available

If a transform cannot carry these forward, the output must reference the file that does.
Provenance is never dropped to save columns.

## Historical vs current

- Never describe historical data as current.
- Do not train a "current" valuation model on old data without an explicit temporal modelling
  strategy. If historical data is used, the model must be labelled as historical-calibrated and
  the temporal gap must be documented.

## Asking price vs transaction price

- Marketplace listings generally represent **asking prices**.
- The product must never call an asking price a verified transaction price.
- Outputs must say "estimated asking price range", not "market price" or "sold price".

## Missing data

- **Unknown is not equivalent to "No".**
- Example: `gas = Unknown` is **not** `gas = No`.
- Missing values must stay missing (or be explicitly imputed with a recorded method), and the
  imputation must be documented.
- Do not invent utility or feature values to fill columns.

## Duplicate listings

- The same property may appear on multiple marketplaces.
- Cross-source duplicates must be investigated before model training.
- Prefer a stable source listing id; otherwise match on normalized URL, normalized location, area,
  bedrooms, bathrooms, price and text similarity.
- Group duplicates with a `duplicate_group_id` instead of silently deleting records.

## Leakage

Do not allow future information to leak into historical model evaluation. Examples to avoid:

- future prices
- future market indices
- post-listing information
- target-derived variables

Any feature that would not have been available at prediction time must be excluded.

## Temporal validation

- The model should eventually use time-aware validation (for example a time-based holdout).
- Market index/reference data is for context and reporting, not as a training signal.

## Outliers

Do not blindly delete unusual properties. Investigate whether each is:

- a legitimate luxury property
- a data-entry error
- a unit error (Marla/Kanal/sqft confusion)
- a duplicate listing
- an unusual property type

Document the decision and keep the record unless there is a clear reason to remove it.

## Data licensing / access

- Only use data obtained through permitted, public or licensed mechanisms.
- Do not bypass CAPTCHA, authentication, paywalls, anti-bot controls, access restrictions or rate
  limits.
- Verify each source's current terms and robots rules before collecting.
- Do not collect personal contact data (phone numbers, emails, CNICs) for the ML dataset.
- If access or licensing is unclear, document the uncertainty and do not collect until resolved.

## Storage and immutability

- Raw captures are append-only and timestamped; a new collection creates a new file, it does not
  overwrite an old one.
- Processed files are disposable: they can always be regenerated from raw.
- Filenames should make the source and date obvious.

## Quality gates before modelling

No dataset enters training until it passes:

1. provenance present for every row;
2. category and dates recorded;
3. normalization rules applied and documented;
4. duplicates grouped;
5. missing-value policy applied;
6. outlier review completed;
7. leakage review completed.

## Personal data

- Do not collect or store personal contact information (names, phone numbers, emails, CNICs) or
  anything else that could identify an individual seller or agent.
- If a source's public page exposes such information, exclude it from stored records.

## Reporting and disclosure

When presenting data-driven results, always state:

- the data window (collection / listing date range);
- the sample size and coverage;
- known limitations and gaps;
- whether the value is an asking-price estimate, a model output or an observed listing.

Never present a model output, a reference index or a historical snapshot as if it were a live,
observed market fact.

