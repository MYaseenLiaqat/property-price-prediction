# Live data collection plan

## Phase 1: licensed baseline
Use Open Data Pakistan's CC Attribution dataset to establish the reproducible baseline.

## Phase 2: current listing collection
For each marketplace, first verify:
- current Terms of Service
- robots.txt / automated access rules
- whether public listing pages may be collected
- whether reuse/redistribution is permitted

Do not bypass CAPTCHA, authentication, rate limits, paywalls, bot defenses or access controls.
Do not collect phone numbers, emails or other personal contact data unless strictly necessary and legally permitted.

## Candidate sources
- Zameen
- Lamudi
- Graana
- RealProperty
- other Lahore marketplaces discovered during research

## Recommended schema
source, listing_id, url, collected_at, purpose, property_type,
city, locality, phase, block, price_pkr, area_value, area_unit,
area_sqft, covered_area_sqft, bedrooms, bathrooms, floors,
property_age, parking, furnished, basement, servant_quarters,
lawn, terrace, electricity, gas, water, sewerage, solar,
latitude, longitude, description_features

## Cross-source deduplication
Prefer a stable source listing ID.
Otherwise compare normalized URL, normalized location, area, beds, baths, price and text similarity.
Keep a `duplicate_group_id` rather than silently deleting provenance.

## Train/test discipline
Use:
- a time-based holdout when dates are available
- location/group-aware validation where appropriate
- a final untouched test set
- MAE/RMSE/median AE/R2
- calibration for prediction intervals
