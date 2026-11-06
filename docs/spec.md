# Build: AV Market Expansion Strategy (robotaxi next-market recommendation)

## 0. Read this first

You are building a portfolio project for a **Strategy Analyst** application at an autonomous-vehicle company. The audience is a strategy team, not engineers. The project must end in a **clear recommendation** ("enter these metros next, in this order, because..."), with the code underneath it.

**The question the project answers:**
A Level 4 robotaxi operator has proven its service in **Las Vegas** and runs on a ride-hail platform partner. Which US metros should it enter next, in what order, and what will each one take?

**How the answer is built:** score 25 candidate metros on the five criteria the AV industry uses to pick launch markets, estimate demand and unit economics for each, test how stable the ranking is, and deliver the result as an interactive app, an executive memo and a slide deck.

### Ground rules (follow these at every step)

1. **Work phase by phase.** At the end of each phase, stop, print the phase checklist with pass/fail for each item, commit to git, and wait for me to type `continue`. Never start the next phase on your own.
2. **Inspect the data at every step.** After every ingestion or transformation, write a short profile to `data/profiles/<step>.md`: row count, columns and types, null counts, min/max/median for numeric columns, 5 sample rows, and the sanity checks listed for that step. Show me the profile summary in chat before moving on.
3. **Never fabricate data.** No mock, synthetic or "placeholder" values anywhere in the pipeline. If a source fails or a field is missing, stop and tell me what failed and what you propose. Do not silently fill gaps.
4. **Every hand-built row needs a source.** Any CSV you assemble by research must have `source_url`, `source_title`, `as_of_date` and `confidence` (`high` / `medium` / `low`) columns. If you can't verify a fact from a source you actually opened, leave the row out and list it under "needs human review" in the profile.
5. **Every assumption is labeled.** Unit-economics inputs live in `config/assumptions.yaml`, each with `value`, `low`, `high`, `source_url` (or `"analyst assumption"`) and a one-line rationale.
6. **Keep the operator generic.** No company logos or company names for the operator in the app, memo or deck. Refer to "the operator" and "the Las Vegas beachhead". Competitors (Waymo, Zoox, Tesla, etc.) can be named because they are public facts.
7. **Don't overclaim.** NHTSA crash reports have no mileage, so never compute or display crash *rates*. Use them only as evidence of where operators are active (see Phase 1).
8. **Keep it simple.** No auth, no live API server, no ML beyond what's specified. Clarity beats cleverness. Anyone should be able to explain the scoring in two minutes.

---

## 1. Repo layout

```
av-expansion-strategy/
├── README.md
├── Makefile                 # make data | make score | make app | make memo | make deck | make all
├── pyproject.toml           # Python 3.11, pandas, requests, pyyaml, duckdb, python-pptx, matplotlib, pytest
├── config/
│   ├── metros.yaml          # the 25 candidates + Las Vegas benchmark
│   ├── weights.yaml         # pillar + sub-metric weights and scenarios
│   └── assumptions.yaml     # unit-economics assumptions (Phase 3)
├── data/
│   ├── raw/                 # untouched downloads (gitignored if large)
│   ├── seed/                # hand-built, sourced CSVs (committed)
│   ├── interim/             # cleaned parquet per source
│   ├── profiles/            # data profiles per step (committed)
│   └── output/              # metros_scored.json etc.
├── pipeline/                # ingest_*.py, build_features.py, score.py
├── dbt/                     # Phase 2
├── analysis/                # Phase 3: demand.py, unit_economics.py, monte_carlo.py
├── reports/                 # Phase 4: memo.md, deck.pptx, charts/
├── app/                     # Vite + React + TypeScript + Recharts + Tailwind
├── tests/
└── docs/
    ├── data_sources.md
    └── methodology.md
```

---

## 2. Metros

Benchmark (scored but not ranked): **Las Vegas**.

Candidates (25): New York, Los Angeles, Chicago, Dallas–Fort Worth, Houston, Washington DC, Philadelphia, Miami, Atlanta, Boston, Phoenix, San Francisco, Detroit, Seattle, Minneapolis, San Diego, Tampa, Denver, Orlando, Charlotte, San Antonio, Austin, Nashville, Pittsburgh, Sacramento.

For each, store in `config/metros.yaml`: display name, CBSA code, principal city name, principal city Census place FIPS (state + place), state abbreviation, latitude/longitude of the principal city's downtown, and primary airport IATA code(s).
**Look the CBSA and place codes up from Census sources. Don't type them from memory.** Profile check: 26 rows, no duplicate codes, every code resolves in the Census API.

---

## 3. Data sources

Document every source in `docs/data_sources.md`: URL, what it contains, the fields used, the vintage, any known caveats, and the date pulled.

| Pillar | Source | Notes |
|---|---|---|
| Demand | **Census ACS 5-year API** (`api.census.gov`), latest vintage available | Metro (CBSA) level for scale; principal-city (place) level for the metrics a launch geofence actually serves. Confirm every variable code against that vintage's `variables.json` before use. |
| Demand | **Census Gazetteer** files (places) | Land area in square miles, for density |
| Demand | **FAA CY passenger boarding (enplanement) data**, latest calendar year | Map airports to metros by IATA code |
| Operating conditions | **Open-Meteo Historical Weather API** (`archive-api.open-meteo.com/v1/archive`) | Daily data, last 10 full calendar years, principal-city coordinates |
| Regulation | **Seed CSV you research**: `data/seed/state_av_regulation.csv` | One row per state covering the 26 metros |
| Competition | **Seed CSV you research**: `data/seed/competitor_presence.csv` | One row per (metro, competitor) |
| Competition check | **NHTSA Standing General Order ADS incident reports (CSV)** | Find the current ADS CSV from the NHTSA SGO crash-reporting page; files have been reorganized into archives, so confirm the current file and its data-element definitions PDF |
| Charging cost | **EIA average retail electricity price by state, commercial sector** (Electric Power Monthly, Table 5.6.A or the EIA API) | Latest 12-month average; seed CSV is fine if the API needs a key |
| Demand calibration (Phase 3) | **Chicago Transportation Network Providers trips** (data.cityofchicago.org) and **NYC TLC high-volume FHV data** | Use aggregated monthly counts (SoQL `count` queries, TLC aggregate reports). Do not download full trip-level files. |

---

## 4. Phases

### Phase 0: Setup and data reconnaissance (no scoring yet)

1. Scaffold the repo, Makefile, pyproject, `.gitignore`, and `git init`.
2. Build `config/metros.yaml` (Section 2).
3. For **every** source in Section 3: confirm it's reachable, pull a small sample, and record the exact fields and vintage in `docs/data_sources.md`.
4. Print a recon table in chat: source, reachable (Y/N), vintage, fields confirmed, blockers.

**Checklist:** all sources reachable or a blocker explained · metros.yaml validated · data_sources.md complete. **Stop.**

---

### Phase 1: Core scoring + React app

**1a. Ingest** (one script per source in `pipeline/`, raw → `data/raw`, cleaned → `data/interim/*.parquet`).

| Script | Output fields | Sanity checks for the profile |
|---|---|---|
| `ingest_acs.py` | metro population; principal-city population, households, households with no vehicle, workers 16+, taxi/ride-hail commuters, median household income | NYC metro population is roughly 19–20M; all 26 metros present; shares between 0 and 1 |
| `ingest_gazetteer.py` | principal-city land area (sq mi) → density | Density is highest for NYC, then SF, Boston or Chicago |
| `ingest_faa.py` | annual enplanements per metro (summed across mapped airports) | Atlanta (ATL) is among the highest; Las Vegas (LAS) is high relative to its population |
| `ingest_weather.py` | per metro, 10-yr annual averages of: rain days (precip ≥ 2.5 mm), snow days (snowfall ≥ 1 cm), extreme-heat days (max temp ≥ 40 °C) | Phoenix and Vegas have the most heat days and few rain days; Minneapolis, Boston and Detroit lead snow days; Miami and Florida metros have zero snow days |
| `ingest_nhtsa.py` | ADS incidents, deduplicated to the **latest version per Report ID** and one row per **Same Incident ID**, last 24 months, mapped to metros by city/state; counts by operating entity × metro | Profile the top operating entities and top cities; list unmapped cities |
| `ingest_eia.py` | commercial ¢/kWh by state | Values fall in a plausible range (roughly 8–30 ¢/kWh) |

**Seed CSVs (research these, following ground rule 4):**

`state_av_regulation.csv`: `state, tier (0–3), driverless_commercial_allowed (Y/N/unclear), permit_body, key_law_or_rule, notes, source_url, source_title, as_of_date, confidence`
- Tier 3: driverless commercial service explicitly allowed and operating in practice
- Tier 2: driverless deployment allowed by law, with a permit process
- Tier 1: testing allowed; driverless commercial deployment unclear or restricted
- Tier 0: restrictive, or no legal pathway

`competitor_presence.csv`: `metro, competitor, status (operating_public | operating_limited | testing | announced), first_public_date, platform_partner, source_url, source_title, as_of_date, confidence`

Cross-check: in the profile, compare `competitor_presence` against NHTSA activity by metro. Flag metros where NHTSA shows activity the seed file lacks, and announced metros with no NHTSA activity. Put this table in the profile. It's a key insight for the memo.

**1b. Features + scoring** (`pipeline/build_features.py`, `pipeline/score.py`)

Sub-metrics, with direction (+ is good, − is bad):

| Pillar | Default weight | Sub-metrics (weight within pillar) |
|---|---|---|
| Market demand | 35 | log metro population + (30) · principal-city density + (25) · taxi/ride-hail commute share + (20) · no-vehicle household share + (15) · enplanements per metro resident + (10) |
| Operating conditions | 25 | rain days − (40) · snow days − (40) · extreme-heat days − (20) |
| Regulatory readiness | 20 | state tier + (100) |
| Competitive intensity | 15 | crowding − (100), where crowding = Σ status weight per competitor (operating_public 1.0, operating_limited 0.7, testing 0.4, announced 0.3) |
| Charging cost | 5 | commercial ¢/kWh − (100) |

Rules:
- Normalize each sub-metric to 0–100 by **percentile rank across the 25 candidates** (robust to NYC-type outliers), flipping the direction where it's −. Score Vegas on the same scale but exclude it from the ranks.
- Pillar score = weighted mean of its sub-metrics. Total = weighted mean of the pillars.
- **Opportunity** = demand pillar. **Ease of entry** = weighted mean of the other four pillars, re-normalized.
- **Vegas similarity** (0–100): 100 minus scaled Euclidean distance to Vegas on standardized [rain days, snow days, heat days, density, enplanements per resident]. Shown as context, not part of the total.
- Scenarios in `config/weights.yaml`, each pillar set summing to 100:
  - `balanced` (default above)
  - `fast_growth`: demand 50, operating 20, regulatory 15, competition 10, charging 5
  - `low_risk`: demand 20, operating 35, regulatory 30, competition 10, charging 5
  - `capital_light`: demand 25, operating 25, regulatory 20, competition 20, charging 10
- For each metro, auto-generate three plain-English "why" bullets: the top two pillar strengths and the single biggest risk (e.g., "Snow on ~X days a year: needs winter validation before launch").

Output `data/output/metros_scored.json`: per metro, raw metric values, normalized sub-scores, pillar scores, total, rank per scenario, opportunity, ease of entry, Vegas similarity, why-bullets, competitors, regulatory tier, plus a `meta` block (data vintages, generated_at, weights).

Tests (`tests/`): weights sum to 100; scores within 0–100; deterministic output; with weights set to 100% weather, Phoenix or San Diego ranks above Minneapolis.

Profile check: print the top 10 for every scenario and how far each metro moves between scenarios. Tell me if anything looks implausible before building the app.

**1c. React app** (`app/`, Vite + React + TypeScript + Recharts + Tailwind; reads `metros_scored.json` copied to `app/public/`)

The page header states the question and the current top-5 recommendation in one sentence. It has three views:
1. **Ranking:** a table of rank, metro, total, five pillar mini-bars, regulatory tier and competitor count. Scenario preset buttons and five pillar weight sliders (always sum to 100; show the live total). Scores **recompute in the browser** from the normalized sub-scores.
2. **Opportunity vs. Ease of Entry:** a 2×2 scatter with median lines, quadrant labels ("Launch next", "Build case", "Opportunistic", "Deprioritize"), bubble size by competitor crowding, and Vegas shown as a distinct reference marker.
3. **Metro drill-down:** a pillar breakdown chart, raw metric values with units, why-bullets, competitors with status, regulatory notes with a source link, and Vegas similarity.

Footer: data vintages and a "Methodology" link to `docs/methodology.md`.
Test: a Vitest test confirming the browser's balanced-scenario scores match Python's to 2 decimal places.
Design: clean, executive, light theme, one accent color, readable on a laptop at 100% zoom, no clutter.

**Phase 1 checklist:** all ingests profiled · seed CSVs fully sourced · cross-check table done · pytest + vitest pass · `make all` runs from scratch · app runs with `npm run dev` · README has a quick start and screenshots. **Stop.**

---

### Phase 2: Production hardening

1. Move transformations into **dbt-duckdb**: `staging` (one model per source) → `intermediate` (features) → `marts` (`mart_metro_scores`). Python ingest stays as-is and lands raw files that dbt reads.
2. dbt tests: `not_null` and `unique` on keys, `accepted_values` for tiers and statuses, range tests on shares and scores.
3. **Parity check:** the dbt mart totals must equal the Phase 1 Python scores to 2 decimal places. Fail loudly if they don't.
4. GitHub Action: a monthly scheduled run (after NHTSA's mid-month release) plus manual dispatch. It runs the pipeline, runs the tests and commits the refreshed JSON.
5. No deployment. The app runs locally only (`npm run dev`, plus `npm run build && npm run preview` to confirm the production build works). Show "data as of" in the header.

**Checklist:** dbt build green · parity passes · Action file valid · production build runs locally. **Stop.**

---

### Phase 3: Demand and unit economics

1. **Demand calibration** (`analysis/demand.py`): pull annual ride-hail trip counts for Chicago and NYC (aggregated queries only). Compute trips per principal-city resident for each, then estimate other metros by scaling with a demand index built from ACS density, taxi/ride-hail commute share, no-vehicle share and enplanements per resident. Report low/base/high from the spread between the two anchors. Write the method and its limits in `docs/methodology.md`: two anchors, and this is an estimate, not a forecast. Profile check: estimates for NYC and Chicago reproduce their observed values; Vegas trips per resident are high relative to its size.
2. **Unit economics** (`analysis/unit_economics.py`, inputs only from `config/assumptions.yaml`): addressable robotaxi trips per day (estimated trips × capture share), fleet needed (÷ trips per vehicle per day), annual revenue per vehicle (trips × average fare), annual operating cost per vehicle (miles × cost per mile, plus charging cost from the EIA price × kWh per mile), contribution per vehicle, payback period on vehicle cost. Output low/base/high for each metro.
3. **Monte Carlo** (`analysis/monte_carlo.py`): sample 10,000 pillar weight sets from a Dirichlet distribution centered on the balanced weights (seeded). Output each metro's share of runs in the top 5 and its median rank.
4. Add to the JSON and the app: a **Unit Economics** panel in the drill-down (with assumption sliders for fare, capture share and trips per vehicle per day) and a **Confidence** column (% of runs in the top 5).

**Checklist:** every assumption sourced or labeled · calibration reproduces the anchors · Monte Carlo seeded and reproducible · tests pass. **Stop.**

---

### Phase 4: Executive outputs

1. `reports/memo.md` (one page, generated from the JSON by a template script):
   - Recommendation (2–3 sentences: the launch sequence)
   - Why these metros (one line each)
   - What we'd deprioritize and why
   - Key risks and how to de-risk (regulation, weather validation, competitive crowding)
   - Confidence (Monte Carlo) and what would change the answer
   - Data and methodology note with vintages
2. `reports/deck.pptx` via python-pptx, 7 slides, charts rendered with matplotlib at 200 dpi:
   1. Title + one-line answer
   2. The question and the five criteria
   3. Opportunity vs. Ease of Entry 2×2
   4. Recommended launch sequence (waves 1–3, with timing logic)
   5. Unit economics for the top 5
   6. Risks and mitigations
   7. Appendix: methodology and sources
   Use one clean template: large titles, one message per slide, the takeaway as the slide title (e.g., "Phoenix and Dallas offer the best mix of demand and ease of entry"), and no paragraph text.
3. `make memo` and `make deck` regenerate both from the latest data.

**Checklist:** memo fits on one page · deck opens without errors · all numbers trace to the JSON · README updated with the final recommendation. **Stop.**

---

## 5. README requirements

- One-paragraph problem statement and the current recommendation at the top
- Screenshots of the three app views
- Architecture diagram (Mermaid): sources → ingest → dbt/DuckDB → JSON → app / memo / deck
- Quick start (`make all`, `npm run dev`)
- Methodology summary and the link to `docs/methodology.md`
- Data sources table with vintages
- Limitations: public data only; NHTSA reports aren't rates; regulation and competitor status are as of the stated date; demand is an estimate from two anchors

## 6. RUN MODE: continuous (overrides the "stop and wait" rule)

- Run all phases (0 → 1 → 2 → 3 → 4) back to back without waiting for me to type "continue".
- Everything else stays the same: write every data profile, run every sanity check and test, keep every sourcing rule, and commit to git at the end of each phase.
- At the end of each phase, print the checklist and a short summary in chat, then move straight on to the next phase.
- Stop and ask me ONLY if:
  1. a data source is unreachable or its schema doesn't match what's expected,
  2. a sanity check or test fails and you can't fix it without changing the methodology,
  3. a parity check fails (browser vs Python, or dbt vs Python),
  4. a decision would change the scoring method, weights, or the metro list.
- Never skip a check to save time. Correct beats fast.
- No deployment and no git push: everything runs locally. Write the GitHub Action file, but don't try to run it.
- When everything is done, give me a final report: what was built, any items under "needs human review", the top-5 recommendation, and the exact commands to run the app locally.

## 7. Start now

Begin with **Phase 0**. Before writing code, restate the plan in five bullets and list any source you expect to be a problem.