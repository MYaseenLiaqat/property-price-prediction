# Lahore PropertyAI data sources

## Primary / training sources
1. Open Data Pakistan — Zameen Property Data
   - URL: https://opendata.com.pk/dataset/property-data-for-pakistan
   - License shown by the publisher: Creative Commons Attribution.
   - Historical snapshot; use as a reproducible baseline, not as current market truth.

2. Zameen.com
   - Public Lahore sale/rent listing pages and Zameen Index.
   - Current listing data is time-sensitive and subject to the site's terms and access rules.
   - Do not collect personal contact details for the ML dataset.

3. Lamudi.pk
   - Public Lahore sale/rent listing pages.
   - Respect current terms, robots rules and access restrictions.

4. Graana.com
   - Public marketplace with Lahore inventory.
   - Respect current terms, robots rules and access restrictions.

5. RealProperty.pk
   - Public Lahore residential listing pages.
   - Respect current terms, robots rules and access restrictions.

6. Landomo
   - Aggregates listings from many portals.
   - Useful as a discovery/coverage benchmark, but its aggregated data should not automatically be treated as licensed for redistribution.

## Reference / market context
- Zameen Index pages provide area-level price and trend benchmarks.
- These benchmark values should be kept separate from listing-level training data to avoid leakage.

## Data policy
The project stores `source`, `source_url`, `collected_at`, and `listing_id` where available.
Do not store phone numbers, emails, CNICs, or other unnecessary personal information.
Before collecting live data, verify the current source terms and permitted use.
