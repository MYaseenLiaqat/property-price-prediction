# Lahore PropertyAI data sources

## Primary / training source

### Zameen Property Data.csv

- **Source organization:** Open Data Pakistan
- **Dataset name:** Zameen Property Data.csv
- **Dataset page:** https://opendata.com.pk/dataset/property-data-for-pakistan
- **Resource URL:** https://opendata.com.pk/dataset/property-data-for-pakistan/resource/2cb1eeea-8dff-41b4-845f-28b8d75ca23b
- **License:** Creative Commons Attribution, as stated by the publisher
- **Original dataset date:** Last updated 2020-05-15 according to the publisher
- **Download/collection date:** Recorded in `historical_lahore_data_report.json` when the local
  raw file is downloaded or inspected
- **Geographic coverage:** Pakistan, including Lahore, Islamabad, Karachi, Rawalpindi and
  Faisalabad records
- **Observed listing period:** The source `date_added` field contains 2019 dates. This is a
  historical snapshot and not a current 2026 feed.
- **Intended use in this project:** Reproducible bootstrap data foundation and historical
  Lahore house-sale model benchmark only.
- **Known limitations:** The dataset is an old marketplace listing snapshot; it contains asking
  prices rather than verified transaction prices, has no current inventory, has no Lahore rent
  rows in the downloaded snapshot, and does not provide the provenance and temporal coverage
  required for a current-market model.

The raw CSV is downloaded to `data/raw/zameen_property_data.csv` and is ignored by Git.
Generated reports record the observed schema, counts, missingness, filtering and limitations.

Historical listing data must remain distinct from current market data. A listing price is an
asking price, not a verified transaction price. Model outputs based on this source must be
described as historical-data estimates and must not be presented as current 2026 market truth.

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
