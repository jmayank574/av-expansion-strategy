# Methodology

The question: a Level 4 robotaxi operator has proven its service in Las Vegas and runs on a ride-hail platform partner. Which US metros should it enter next, in what order, and what will each one take?

The answer is built in four steps: score 25 candidate metros on five criteria, estimate demand and unit economics, test how stable the ranking is, and present the result.

## 1. The five criteria (pillars)

| Pillar | Default weight | Sub-metrics (weight within pillar) | Direction |
|---|---|---|---|
| Market demand | 35 | log metro population (30), principal-city density (25), taxi/ride-hail commute share (20), no-vehicle household share (15), airport enplanements per metro resident (10) | higher is better |
| Operating conditions | 25 | rain days (40), snow days (40), extreme-heat days (20) | lower is better |
| Regulatory readiness | 20 | state AV regulation tier, 0 to 3 (60); new-entrant path, slow / moderate / fast (40) | higher is better |
| Competitive intensity | 15 | crowding (100) | lower is better |
| Charging cost | 5 | commercial electricity price, cents/kWh (100) | lower is better |

Operator presence (rows flagged `is_operator` in the seed file) is shown in the app but never counted as competition. Crowding = sum over competitors of a status weight: operating_public 1.0, operating_limited 0.7, testing 0.4, announced 0.3.

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
- **Regulation tier** (0-3), the **new-entrant path** (fast / moderate / slow) and **competitor presence** are hand-researched seed CSVs, each row with source URL, title, date and confidence. Rows that could not be verified from a page that was opened were dropped and listed in `data/profiles/07_seed_and_crosscheck.md`.
- **NHTSA SGO ADS reports** are used only as evidence of where operators are active, never as rates, because the reports carry no mileage. Reports are reduced to the latest version per Report ID, then one row per Same Incident ID, over the last 24 months. Cities are mapped to metros by principal-city name, then by Census Gazetteer city point within 40 km of downtown (for suburbs such as Tempe), plus three explicit aliases (Venice, Fort Worth, Kingwood).

### Regulatory readiness: legal tier and new-entrant path

The regulatory pillar has two sub-metrics, both percentile-ranked like every other: **state tier** (0-3, weight 60) says whether driverless commercial service is legal; **new-entrant path** (weight 40) says how quickly a *new* operator could reach paid driverless service in that state. Other pillar and sub-metric weights are unchanged.

New-entrant path (`data/seed/state_av_regulation.csv`, each row sourced to a page that was opened):

- **fast**: one registration, filing or authorization with no discretionary review and no separate passenger-fare permit, and an operator has already launched under it (AZ, TX, FL, GA, TN, CO).
- **moderate**: two agencies or a discretionary approval, or a paper path with no commercial precedent (NV needs a DMV certificate plus a Transportation Authority permit; WA, NC and MI have light statutes but no paid driverless precedent).
- **slow**: three or more sequential approvals including a separate fare permit (CA: DMV testing, driverless testing and deployment permits plus CPUC pilot and deployment programs; PA: supervised testing, PennDOT certification, PUC approval), or a law change is needed first (NY, MA, MN, IL, DC).

The path is an analyst classification from the cited statutes and regulator pages, not an official rating.

## 4. Known limitations

- Public data only. Regulation and competitor status are as of 2026-11-06 and change fast.
- Percentile ranking on a 0-3 tier compresses the regulatory pillar: with many metros tied at Tier 3, a Tier 3 state scores about 73, not 100. The ordering is preserved.
- Percentile ranking says how a metro compares with the other 24, not how good it is in absolute terms.
- The balanced total rewards demand heavily. The largest, densest markets (San Francisco, Los Angeles) rank high even though competitors are already active there. The Opportunity vs. Ease of Entry view and the scenarios show this trade-off.
- Competitor status was researched from opened pages on 2026-11-06 (see the notes in `data/profiles/07_seed_and_crosscheck.md`). The waymo.com access page is undated and lags press reports for some cities; Tesla Miami, Phoenix, Las Vegas, Orlando and Tampa rest partly on a fan site; Avride Austin rests on Wikipedia. Rows are marked medium or low confidence accordingly.
- NHTSA city-to-metro mapping is approximate for small suburbs; unmapped cities are listed in the profile.

## 5. Demand calibration (Phase 3)

Two anchors, one estimate. This is an estimate from two cities, not a forecast.

1. **Anchors (calendar 2025).** Chicago: Transportation Network Providers trips, 93.5M, from the City of Chicago data portal using a SoQL count (no trip rows downloaded). New York: High Volume FHV trips, 243.6M, taken as row counts from the TLC monthly parquet files' footers (metadata only, no trip rows downloaded). Divided by principal-city population (ACS 2024), that gives 34.5 trips per resident in Chicago and 28.7 in New York.
2. **Demand index.** The geometric mean of principal-city density, taxi/ride-hail commute share, no-vehicle household share and enplanements per metro resident.
3. **Scaling.** Each metro's trips per resident is the anchor's trips per resident times the ratio of demand indexes, done once from each anchor. Low and high are the smaller and larger of the two; base is their geometric mean. The two anchor cities report their observed values.
4. **Limits.** The anchors disagree with the index: Chicago has more trips per resident than New York despite a lower index. That makes the low-to-high spread wide (about 1.3x each way from base). Two points cannot identify an elasticity, so the scaling is proportional. Chicago TNP data counts pickups within city limits and includes shared trips; NYC data covers the five boroughs and licensed high-volume FHV apps. Estimated trips are for the principal city, since that is where a launch geofence would operate.

## 6. Unit economics (Phase 3)

Inputs come only from `config/assumptions.yaml`. Each has a value, a low (pessimistic) and a high (optimistic) end, and a rationale. All are labeled analyst assumptions: none comes from a published source. Only the electricity price (EIA, by state) and the demand estimate come from data.

- Addressable robotaxi trips per day = estimated annual ride-hail trips x capture share / 365.
- Fleet needed = trips per day / paid trips per vehicle per day.
- Revenue per vehicle = trips per vehicle per day x 365 x average fare.
- Operating cost per vehicle = vehicle miles x cost per mile + vehicle miles x kWh per mile x state commercial price. Vehicle miles = paid miles / (1 - deadhead share).
- Contribution = revenue - operating cost. Payback = vehicle cost / contribution (shown as "never" if contribution is not positive).

The low / base / high outputs apply the pessimistic / central / optimistic end of every input together, so they are a stress range, not a statistical interval. Because fare, cost per mile and utilization are the same in every metro, per-vehicle payback varies little across metros (only the power price differs): base-case payback is 2.2 to 2.4 years everywhere. Public per-metro fare or trip-length data exists only for the two calibration anchors (Chicago and NYC), so fare is not varied by metro. Stress range (every input pessimistic, or every input optimistic, at once): payback of 0.7-0.7 years in the high case and 43-276 years in the low case, i.e. effectively never. Read payback as assumption-driven; read fleet size and revenue pool as the demand-driven outputs. Demand mainly sets the fleet size. The app lets a reader change fare, capture share and trips per vehicle per day.

## 7. Monte Carlo on the weights (Phase 3)

10,000 pillar-weight sets are drawn from a Dirichlet distribution centered on the balanced weights (concentration 50, seed 42), which moves each weight by roughly 5 to 7 points. For each draw all 25 candidates are re-ranked. The Confidence column in the app is the share of draws in which the metro lands in the top 5; the median rank is also reported. Concentration is an analyst choice: a lower value would explore more extreme weightings. This tests weight uncertainty only, not data error or assumption error.

## 8. From scores to a launch sequence (Phase 4)

The memo and deck derive the sequence from `data/output/metros_scored.json` with fixed rules (`reports/plan.py`):

- **Wave 1:** balanced rank 1-5, state regulation tier 2 or higher, and top 5 in at least 50% of Monte Carlo weight draws.
- **Wave 2:** remaining metros ranked 1-10 in tier 2+ states.
- **Wave 3:** remaining metros ranked 1-10 in tier 0-1 states. These are policy-dependent options: build the case, launch when driverless commercial service becomes legal.
- **Deprioritize:** balanced rank 18 or lower. Their best rank in any of the four scenarios is reported alongside.

Timing is stated as evidence gates (rules, proof from the earlier wave), not calendar dates. The thresholds (50%, rank 10, rank 18) are analyst choices and are visible in the code.
