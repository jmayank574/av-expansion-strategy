# Methodology

The question: a Level 4 robotaxi operator has proven its service in Las Vegas and runs on a ride-hail platform partner. Which US metros should it enter next, in what order, and what will each one take?

The answer is built in four steps: score 25 candidate metros on five criteria, estimate demand and unit economics, test how stable the ranking is, and present the result.

## 1. The five criteria (pillars)

| Pillar | Default weight | Sub-metrics (weight within pillar) | Direction |
|---|---|---|---|
| Market demand | 35 | log metro population (30), principal-city density (25), taxi/ride-hail commute share (20), no-vehicle household share (15), airport enplanements per metro resident (10) | higher is better |
| Operating conditions | 25 | rain days (40), snow days (40), extreme-heat days (20) | lower is better |
| Regulatory readiness | 20 | state AV regulation tier, 0 to 3 (100) | higher is better |
| Competitive intensity | 15 | crowding (100) | lower is better |
| Charging cost | 5 | commercial electricity price, cents/kWh (100) | lower is better |

Crowding = sum over competitors of a status weight: operating_public 1.0, operating_limited 0.7, testing 0.4, announced 0.3.

## 2. Scoring in two minutes

1. Each sub-metric is turned into a 0-100 score by **percentile rank across the 25 candidates** (the lowest candidate gets 0, the highest 100, ties share the average rank). Where lower is better the score is flipped (100 minus the percentile). Percentile ranks are robust to outliers such as New York.
2. A pillar score is the weighted mean of its sub-scores.
3. The total is the weighted mean of the five pillars.
4. **Opportunity** is the demand pillar. **Ease of entry** is the weighted mean of the other four pillars, with weights re-normalized to sum to 100.
5. Las Vegas is scored on the same scale (its raw values are placed on the candidates' percentile curve by interpolation) but is never ranked and does not affect anyone else's score.
6. **Vegas similarity** (0-100) = 100 minus the Euclidean distance to Las Vegas on standardized [rain days, snow days, heat days, density, enplanements per resident], scaled so the most distant candidate scores 0. It is context only and is not in the total.

Scenarios (`config/weights.yaml`): balanced 35/25/20/15/5, fast growth 50/20/15/10/5, low risk 20/35/30/10/5, capital light 25/25/20/20/10 (demand/operating/regulatory/competition/charging).

Rank ties share the best rank. Totals are rounded to 9 decimals before ranking so that floating-point noise cannot break a tie differently in Python and in the browser.

## 3. Inputs and how they were built

See `docs/data_sources.md` for URLs, vintages and caveats. Notes on choices:

- **Demand** uses ACS 5-year 2024 at metro (CBSA) level for scale and at principal-city (place) level for density, no-vehicle share and ride-hail share, since a launch geofence serves the city core. Land area comes from the 2025 Census Gazetteer.
- **Weather** is the 10-year (2016-2025) annual average of days with precipitation >= 2.5 mm, snowfall >= 1 cm, and max temperature >= 40 C, from Open-Meteo reanalysis at a downtown point. It is gridded model data, not station data.
- **Downtown coordinates** are Open-Meteo geocoding (GeoNames) city-center points. The Census Gazetteer internal point was rejected because it is not a downtown (San Francisco's falls in the Pacific).
- **Enplanements** are FAA CY2025, summed over the airports mapped to each metro. West Palm Beach appears under the FAA identifier DJT.
- **Electricity** is EIA Table 5.6.B, commercial sector, year-to-date through August 2026. It is not a 12-month average. This was a deliberate choice, since the 12-month series needs an API key.
- **Regulation tier** (0-3) and **competitor presence** are hand-researched seed CSVs, each row with source URL, title, date and confidence. Rows that could not be verified from a page that was opened were dropped and listed in `data/profiles/07_seed_and_crosscheck.md`.
- **NHTSA SGO ADS reports** are used only as evidence of where operators are active, never as rates, because the reports carry no mileage. Reports are reduced to the latest version per Report ID, then one row per Same Incident ID, over the last 24 months. Cities are mapped to metros by principal-city name, then by Census Gazetteer city point within 40 km of downtown (for suburbs such as Tempe), plus three explicit aliases (Venice, Fort Worth, Kingwood).

## 4. Known limitations

- Public data only. Regulation and competitor status are as of 2026-11-05 and change fast.
- Percentile ranking on a 0-3 tier compresses the regulatory pillar: with many metros tied at Tier 3, a Tier 3 state scores about 73, not 100. The ordering is preserved.
- Percentile ranking says how a metro compares with the other 24, not how good it is in absolute terms.
- The balanced total rewards demand heavily. The largest, densest markets (San Francisco, Los Angeles) rank high even though competitors are already active there. The Opportunity vs. Ease of Entry view and the scenarios show this trade-off.
- Competitor status tiers for some cities (limited vs. public) are judgments from search extracts; Tesla rows rest on a fan/news site.
- NHTSA city-to-metro mapping is approximate for small suburbs; unmapped cities are listed in the profile.
