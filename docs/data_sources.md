# Data sources

First recon pulled 2026-11-05; the weather source and both seed files were changed or re-researched on 2026-11-06 (see the sections at the end). Where a row below describes the original recon and a later section supersedes it, the row says so.

| # | Source | URL | Contents / fields to use | Vintage | Status | Caveats |
|---|---|---|---|---|---|---|
| 1 | Census ACS 5-year API | `https://api.census.gov/data/2024/acs/acs5` | metro and place population, households, no-vehicle households, workers, taxi/ride-hail commuters, median HH income | 2020-2024 5-year (latest) | OK with a free API key (`CENSUS_API_KEY` in `.env`, never committed) | Variables confirmed against the 2024 `variables.json`: B01003_001E, B08201_001E, B08201_002E (no vehicle), B08301_001E, B08301_016E (taxi or ride-hailing), B19013_001E |
| 2 | Census Gazetteer, places | `https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_place_national.zip` | `GEOID`, `ALAND_SQMI`, `INTPTLAT/LONG` | 2025 | OK | Land area, not total area. Internal point is not downtown (SF falls in the Pacific because of the Farallon Islands) |
| 3 | Census CBSA delineation | `https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx` | CBSA code and title | July 2023 delineation (2024/2025 files not found at the same path) | OK | ACS 2024 uses 2023 delineations, so they match |
| 4 | FAA CY enplanements | `https://www.faa.gov/airports/planning_capacity/passenger_allcargo_stats/passenger/arp-cy2025-commercial-service-enplanements.xlsx` | `Locid`, `CY 25 Enplanements` | CY2025 | OK | West Palm Beach (IATA PBI) is listed as `DJT` in the file. We map Miami to DJT |
| 5 | **NOAA GHCN-Daily** (primary weather source; replaced Open-Meteo on 2026-11-06) | `https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries` | daily `PRCP`, `SNOW`, `TMAX` (metric) at one airport station per metro | 2016-2025 daily | OK | Station IDs are in `config/metros.yaml`. A missing SNOW value counts as no snow. Open-Meteo archive (`https://archive-api.open-meteo.com/v1/archive`, reanalysis grid, not station data) is kept only as a fallback for a station missing more than 5% of days; none needed. See the NOAA section at the end |
| 6 | Open-Meteo geocoding | `https://geocoding-api.open-meteo.com/v1/search` | city-center lat/lon (GeoNames) | live | OK | Used as the downtown proxy in `metros.yaml` |
| 7 | NHTSA SGO ADS incident reports | `https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv` (current, 1,595 rows) and `.../Archive-2021-2025/SGO-2021-01_Incident_Reports_ADS.csv` (2,295 rows) | `Report ID`, `Report Version`, `Reporting Entity`, `Operating Entity`, `Same Incident ID`, `Incident Date`, `City`, `State` | Current file: incidents Apr 2025 to Sep 2026, release dated Sep 2026. Archive: 2021 to Sep 2024 | OK | Two files with **different schemas** (116 vs 137 cols). The page `nhtsa.gov/...crash-reporting` returns 403 to scripts, so URLs were found via search. No mileage, so no crash rates. Possible gap between Sep 2024 and Apr 2025 to check. Definitions PDF: `static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Data_Element_Definitions.pdf` |
| 8 | EIA Electric Power Monthly Table 5.6.B | `https://www.eia.gov/electricity/monthly/xls/table_5_06_b.xlsx` | commercial cents/kWh by state | year-to-date through Aug 2026 | OK (table chosen by the user) | A year-to-date average, not a 12-month average. Table 5.6.A is a single month, so it was not used. Hawaii (42.4) and North Dakota (7.7) fall outside 8-30, but no metro is in those states |
| 9 | Chicago TNP trips | Socrata `m6dm-c72p` (2018-22), `n26f-ihde` (2023-24), `6dvr-xwnh` (2025-) at `data.cityofchicago.org/resource/<id>.json` | aggregate with SoQL `count` | 2025 count: 93,514,416 trips (the demand anchor) | Used | One dataset per period. The 2025 count agrees within 0.8% with the city's separate TNP Drivers dataset (`j6wf-834c`), see `docs/validation.md` |
| 10 | NYC TLC HVFHV | monthly trip-record parquet files on `d37ci6vzurychx.cloudfront.net`; only the row counts in each file's footer are read, no trip rows are downloaded | monthly trip counts | 2025: 243,589,684 trips (the demand anchor) | Used | December 2025 (22,108,438) matches the TLC Licensing Review Report exactly; no published annual total was found, see `docs/validation.md`. The TLC aggregated-reports page returned 403 to scripts |
| 11 | Seed: state AV regulation | `data/seed/state_av_regulation.csv` | researched | n/a | Done, 17 states, see profile 07 for low-confidence rows | Each row has a source opened during research |
| 12 | Seed: competitor presence | `data/seed/competitor_presence.csv` | researched 2026-11-06 | n/a | Done, 51 rows covering all 26 metros | Each row sourced to an opened page, with an `is_operator` flag. Some Tesla rows rest on a fan site and Avride Austin on Wikipedia (medium confidence); see profile 07 |

## Final ingest notes
- Census API key: set `CENSUS_API_KEY` in `.env` (copy `.env.example`). The key is gitignored.
- NHTSA: the current file (Apr 2025 to Sep 2026 incidents) and the archive file (to Jun 2025) overlap, with different Report IDs, and are de-duplicated by Same Incident ID. The 24-month window is Oct 2024 to Sep 2026.
- Weather responses (NOAA station files, and the Open-Meteo fallback series) are cached in `data/raw/weather/` (raw is gitignored). Open-Meteo's free tier returns HTTP 429 after a burst of calls, and the ingest retries with a back-off.

## Seed files re-researched 2026-11-06

- `data/seed/competitor_presence.csv`: all 26 metros re-researched from opened company, news, SEC and regulator pages (Waymo, Tesla, Zoox, Avride, May Mobility, Motional, Nuro/Lucid, Lyft/Mobileye). Every row has source URL, title, as-of date and confidence, plus an `is_operator` flag: the operator's own presence (Las Vegas) is shown in the app as "operator presence" and is excluded from the crowding score. Cross-checked against NHTSA SGO activity in `data/profiles/07_seed_and_crosscheck.md`.
- `data/seed/state_av_regulation.csv`: added `new_entrant_path` (fast / moderate / slow) with rationale, source URL, title, as-of date and confidence for each of 17 states. Sources include CPUC, CA DMV, TxDMV, NV DMV and NTA, ADOT statute text, Florida Statutes, and AFDC summaries for Georgia and Tennessee.

## Weather source changed to NOAA GHCN-Daily (2026-11-06)

- `pipeline/ingest_weather.py` now reads NOAA GHCN-Daily station observations from the NCEI Access Data Service
  (`https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries`), daily PRCP, SNOW and TMAX in metric units, 2016-2025.
- One airport station per metro, chosen by `pipeline/lookup_weather_stations.py` from NOAA's `ghcnd-stations.txt` and `ghcnd-inventory.txt`
  (station must have PRCP and TMAX covering 2016-2025) and located within 8 km of the metro's primary commercial airport, using airport
  coordinates from the OurAirports public dataset. The station ID, name and distance from the city point are in `config/metros.yaml`.
- Same thresholds as before: rain >= 2.5 mm, snow >= 10 mm, max temperature >= 40 C. GHCN usually omits SNOW on days without snow, so a missing SNOW value counts as no snow.
- Open-Meteo archive remains only as a documented fallback for any station missing more than 5% of days (none needed on 2026-11-06; worst station 0.6%), and its series is kept as `om_*` columns for comparison.
