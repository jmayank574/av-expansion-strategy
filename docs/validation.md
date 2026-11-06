# External validation

Checked on 2026-11-06 against independent sources that were opened during the check. This is a report only: no pipeline code, config or data was changed.

**Verdicts.** PASS = within tolerance. FLAG = off, or a problem with the evidence, with the reason. UNVERIFIED = no source found that could be opened.

**Method notes.** Numbers were compared in a scratch folder that read the pipeline's outputs read-only. Sources that returned an error (HTTP 403/429, certificate failure, unreadable PDF) are named where they matter, and nothing in this document relies on a page that could not be read. Search-result snippets were used only to find pages, never as evidence.

## Summary

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Metro population vs Census estimates | 4 PASS, 1 FLAG | Matches Census exactly on a like-for-like period; Phoenix is 3.05% below the latest-year estimate |
| 2 | Weather vs NOAA station data | 12 PASS, 3 FLAG | Direction and rank order right; rain days run 20-49% high and heat days 10-22% low versus stations |
| 3 | Electricity price vs EIA table | 5 PASS | Exact |
| 4 | Enplanements vs FAA file | 5 PASS | Exact (metro totals are sums of airports by design) |
| 5 | Ride-hail anchors | 2 PASS, 1 UNVERIFIED | Chicago within 0.8%; NYC December 2025 exact, no published annual total found |
| 6 | Competitor rows, top 10 metros | 18 confirmed, 1 CHANGED | Waymo in Chicago has moved from `announced` to `testing`; correcting it moves six ranks |
| 7 | Regulation, states of the top 10 | 16 PASS, 2 FLAG | Both flags are citation problems, not wrong values |
| 8 | Unit-economics assumptions | 3 PASS | Fare modestly aggressive, cost per mile and trips per vehicle conservative, vehicle cost mid-range |

## 1. Metro population

Source: Census Population Estimates Program, metro/micro totals, vintage 2024 (`cbsa-est2024-alldata.csv`). Ours is ACS 5-year 2020-2024. Tolerance 3%.

| Metro | CBSA | Ours (ACS) | PEP 2020-24 average | vs average | PEP July 2024 | vs 2024 | Verdict |
|---|---|---|---|---|---|---|---|
| New York | 35620 | 19,798,537 | 19,798,539 | 0.0% | 19,940,274 | -0.7% | PASS |
| Los Angeles | 31080 | 12,974,487 | 12,974,487 | 0.0% | 12,927,614 | +0.4% | PASS |
| Chicago | 16980 | 9,371,595 | 9,371,596 | 0.0% | 9,408,576 | -0.4% | PASS |
| Phoenix | 38060 | 5,028,754 | 5,028,754 | 0.0% | 5,186,958 | **-3.05%** | FLAG |
| Las Vegas | 29820 | 2,329,548 | 2,329,548 | 0.0% | 2,398,871 | -2.89% | PASS |

Phoenix is a flag only against the latest single-year estimate, and by 0.05 points. The ACS 5-year figure is controlled to the average of the five annual estimates, so it lags fast-growing metros (Phoenix, Las Vegas). The model ranks log population by percentile, so this has no practical effect on scores.

## 2. Weather

Source: NOAA GHCN-Daily station observations from the NCEI Access Data Service, 1 Jan 2016 to 31 Dec 2025 (3,653 days, no missing precipitation or temperature days at any station). Same thresholds as ours: rain >= 2.5 mm, snow >= 10 mm (1 cm), max temperature >= 40 C. Stations are airport weather stations: Phoenix Sky Harbor USW00023183, Las Vegas USW00023169, Miami Intl USW00012839, Minneapolis-St Paul USW00014922, Boston Logan USW00014739. Tolerance: within about 25%.

| Metro | Rain days: ours / NOAA | diff | Snow days: ours / NOAA | diff | 40 C+ days: ours / NOAA | diff |
|---|---|---|---|---|---|---|
| Phoenix | 24.6 / 16.5 | **+49%** FLAG | 0.0 / 0.0 | PASS | 69.6 / 89.3 | -22% PASS |
| Las Vegas | 12.9 / 10.4 | +24% PASS | 0.2 / 0.1 | PASS (0.1 day) | 55.0 / 60.8 | -10% PASS |
| Miami | 131.9 / 92.0 | **+43%** FLAG | 0.0 / 0.0 | PASS | 0.0 / 0.0 | PASS |
| Minneapolis | 79.5 / 63.6 | +25% PASS | 22.3 / 23.8 | -6% PASS | 0.0 / 0.0 | PASS |
| Boston | 94.8 / 78.8 | +20% PASS | 14.3 / 11.2 | **+28%** FLAG | 0.0 / 0.0 | PASS |

Reading: the direction and the rank order across these five metros are right for all three measures (rain: Miami > Boston > Minneapolis > Phoenix > Las Vegas in both sources; heat: Phoenix > Las Vegas in both). The gap is a level bias: the Open-Meteo archive is gridded reanalysis, which spreads light precipitation over more days than a single airport gauge counts and smooths temperature extremes, so rain days run high and 40 C+ days run low. The model uses percentile ranks, so a consistent level bias matters much less than a rank error would. It does mean the displayed raw values in the app (for example "Phoenix: 25 rain days") should not be read as gauge counts.

## 3. Electricity price

Source: EIA Electric Power Monthly Table 5.6.B, downloaded fresh (`table_5_06_b.xlsx`), commercial column, "August 2026 YTD". Exact match required.

| State | EIA table | Ours | Verdict |
|---|---|---|---|
| CA | 26.96 | 26.96 | PASS |
| TX | 8.60 | 8.60 | PASS |
| FL | 11.78 | 11.78 | PASS |
| AZ | 12.28 | 12.28 | PASS |
| PA | 13.90 | 13.90 | PASS |

This confirms transcription and period. It is the same publisher and table the pipeline used, so it is not an independent estimate of what operators pay. The table is a year-to-date average, not a 12-month average (already stated in `docs/methodology.md`).

## 4. Airport enplanements

Source: FAA CY2025 commercial service enplanements file, downloaded fresh. Exact match required.

| Airport | FAA file | Ours | Verdict |
|---|---|---|---|
| ATL | 51,459,786 | 51,459,786 (Atlanta metro, ATL only) | PASS |
| LAS | 26,531,765 | 26,531,765 (Las Vegas metro, LAS only) | PASS |
| PHX | 25,094,817 | 25,094,817 (Phoenix metro, PHX only) | PASS |
| LAX | 36,497,303 | 47,104,752 (Los Angeles metro = LAX + BUR + LGB + SNA) | PASS |
| MIA | 26,450,972 | 46,354,909 (Miami metro = MIA + FLL + DJT) | PASS |

For LAX and MIA the airport figure in the file is only one component of the metro total. The metro totals equal the sum of the FAA file rows for the mapped airports exactly. Whether Burbank, Long Beach and Orange County belong to the Los Angeles metro, and Palm Beach to the Miami metro, follows the Census CBSA definitions.

## 5. Ride-hail demand anchors

| Anchor | Ours | Independent figure | Diff | Verdict |
|---|---|---|---|---|
| Chicago, 2025 trips | 93,514,416 (City of Chicago TNP Trips, row count) | 92,786,905: sum of `number_of_trips` over 2025-01 to 2025-12 in the city's separate TNP Drivers dataset (`j6wf-834c`) | +0.78% | PASS |
| NYC, 2025 trips | 243,589,684 (sum of the 12 monthly TLC HVFHV files) | NYC TLC Licensing Review Report (Feb 2026), Table 1: December 2025 high-volume FHV trips 22,108,438. Ours for 2025-12: 22,108,438 | 0.0% (one month) | PASS for the month |
| NYC, 2025 annual total | 243,589,684 | No published 2025 annual total found in any page that could be opened | n/a | UNVERIFIED |

Chicago cross-checks: June 2025 is 7,690,883 in the trips dataset vs 7,647,101 in the drivers dataset (+0.57%). A third-party dashboard built from the city data (Tom Slee's Chicago Ridehail Charts, updated 2026-10-30) gives about 248,800 trips per day for September 2025, vs 256,200 per day for our full-year average, which is consistent given seasonality. The drivers and trips datasets are both published by the city, so this tests the count, not the city's own reporting. NYC: TLC's own report is the only official total I could open. The 2025 annual figure of 243.6M is the sum of TLC's monthly files and is consistent with TLC's stated "20+ million trips per month".

## 6. Competitor status, top 10 metros

Top 10 by balanced rank: Miami, San Francisco, Los Angeles, Chicago, Phoenix, New York, Detroit, Atlanta, Philadelphia, Boston. All 12 source URLs behind the 19 rows were re-opened.

| Metro / competitor | Seed status | Re-check | Verdict |
|---|---|---|---|
| Miami / Waymo | operating_public | Waymo blog 2026-04-15: "now open to everyone" | Confirmed |
| Miami / Tesla | operating_limited | Drive Tesla Canada 2026-07-03: unsupervised, nobody in the car (fan site) | Confirmed |
| Miami / Zoox | testing | Electrek 2026-03-24: employees, family and friends first | Confirmed |
| San Francisco / Waymo | operating_public | waymo.com "operates 24/7 from San Francisco down to San Jose" | Confirmed |
| San Francisco / Zoox | operating_limited | Electrek: "not fully public yet", Explorers Program | Confirmed (borderline: invite-based) |
| San Francisco / Tesla | testing | Electrek 2026-04-30: Bay Area runs supervised FSD, not unsupervised Robotaxi | Confirmed |
| San Francisco / Nuro-Lucid | testing | SF Standard 2025-10-29: "on-road development is underway", launch late 2026 | Confirmed (source is 12 months old) |
| Los Angeles / Waymo | operating_public | waymo.com "24/7 across more than 120 square miles" | Confirmed |
| Los Angeles / Zoox | testing | Electrek: "already being mapped and tested" | Confirmed |
| **Chicago / Waymo** | **announced** | **ABC7 Chicago 2026-04-07: Waymo mapping and testing downtown with safety drivers; NPR Illinois 2026-10-22 caption: testing and mapping since March 2026. waymo.com still lists Chicago under Up Next** | **CHANGED: should be `testing`** |
| Phoenix / Waymo | operating_public | waymo.com "24/7 across 315 square miles" | Confirmed |
| Phoenix / Tesla | announced | Drive Tesla Canada 2026-07-03: "preparations underway", not launched | Confirmed (source is four months old) |
| New York / Waymo | testing | Insurance Journal 2026-02-20: test permit, trained specialist behind the wheel | Confirmed |
| Detroit / Waymo | announced | waymo.com Up Next | Confirmed |
| Atlanta / Waymo | operating_public | waymo.com: "available only on Uber in Atlanta" | Confirmed |
| Atlanta / Zoox | testing | Insurance Journal 2025-05-21: safety drivers, mapping, employees only; Electrek 2026-03-24 still lists Atlanta as being mapped and tested | Confirmed |
| Atlanta / May Mobility | operating_limited | May Mobility investor deck: "Launched in September 2025 in Atlanta"; deck does not say whether a safety operator is on board | Confirmed (operator presence not stated) |
| Philadelphia / Waymo | testing | PhillyVoice 2026-10-09: tested with safety drivers since July 2025, "not yet configured for fully autonomous driving" | Confirmed |
| Boston / Waymo | testing | Boston Globe (Feb 2026): returning for testing with human drivers | Confirmed |

**The one change: Chicago.** Correcting Waymo-in-Chicago from `announced` (weight 0.3) to `testing` (weight 0.4) is a 0.1 change in the crowding score, but it moves Chicago from #4 to #9 in the balanced ranking (simulated in memory; nothing was written). Other ranks that move: Phoenix 5 to 4, New York 6 to 5, Detroit 7 to 6, Atlanta 8 to 7, Philadelphia 9 to 8. The waves do not change: Chicago and New York stay in wave 3 (Tier 1), Phoenix stays in wave 1.

**Why a 0.1 change does this.** Crowding takes few distinct values and many metros tie at 0.3 (announced only) or 0.4. Percentile ranking turns a tie group's position into a large step in the competition sub-score (Chicago's competition pillar would drop from 91.7 to 75.0, which is -2.5 points of total, 55.7 to 53.2). The ranking is therefore sensitive to single competitor-status changes near those ties. This is a property of the method, and worth stating when presenting the ranks in positions 4 to 10.

## 7. Regulation, states of the top 10

States: AZ, CA, FL, GA, IL, MA, MI, NY, PA. Each row's tier source and new-entrant-path source was re-opened.

| State | Tier | Path | Re-check | Verdict |
|---|---|---|---|---|
| AZ | 3 | fast | A.R.S. 28-9702: operation allowed "only if a person submits" a law-enforcement plan and a written statement; ADOT may issue a cease-and-desist if missing. Filings, not approval | PASS / PASS |
| CA | 3 | slow | CA DMV: three permit categories (testing with safety driver, driverless testing, deployment). CPUC: four programs, fares only in the two deployment programs, DMV deployment permit a prerequisite | PASS / PASS |
| FL | 3 | fast | Fla. Stat. 316.85: no licensed human operator required; no state permit on the page; on-demand networks must meet s.627.749 insurance | PASS / PASS |
| GA | 3 | fast | AFDC summary: federal standards plus registration as fully autonomous; no permit named. Statute text not opened (confidence medium, as in the seed) | PASS / PASS |
| IL | 1 | slow | ABC7 2026-04-07 and NPR Illinois 2026-10-22: no law authorizes driverless service; HB4663 stalled in the House, HB4789 also stalled; "may come up again in the November veto session". ILGA page failed a certificate check and was not read | PASS / PASS |
| MA | 1 | slow | Boston Globe (Feb 2026), re-opened: "Massachusetts doesn't currently allow fully driverless cars". The seed's State House News page returned HTTP 429 on re-open (it was read earlier the same day). A later search snippet says the bills were disposed of by study order in July 2026; not opened, so not relied on and it would not change the tier | PASS / PASS |
| MI | 2 | moderate | MCL 257.665: operation allowed (subsection 4), insurance proof needed, no separate permit. The section is framed around research and testing, and there is no permit process, so Tier 2 ("allowed by law, with a permit process") is a judgment call between 2 and 3. No driverless commercial precedent in Detroit | PASS / PASS (borderline) |
| NY | 1 | slow | Value correct: Cleantechnica 2026-02-20 says New York has no commercial robotaxi pathway because of the one-hand-on-the-wheel rule, testing exemptions only. **Citation problem:** the seed cites an Insurance Journal article that does not state that driverless operation is illegal | PASS (value) / FLAG (citation) |
| PA | 2 | slow | Path is supported by PhillyVoice 2026-10-09 (PennDOT certification, 10 days' notice to the city, PA PUC approval, not yet certified after 15 months). **Citation problem:** the cited PennDOT guidelines page returned only a headline and navigation, so the tier cannot be confirmed from that page; PhillyVoice supports Tier 2 | PASS (path) / FLAG (tier source) |

## 8. Unit-economics assumptions

Ours are in `config/assumptions.yaml`. All are labelled "analyst assumption"; nothing in the file currently cites a public reference.

| Assumption (low / base / high) | Public reference opened | Comparison | Position |
|---|---|---|---|
| **Average fare $15 / $20 / $25** | Obi pricing data via TechCrunch (2026-01-27), San Francisco Bay Area rides 27 Nov to 1 Jan: Waymo $19.69, Uber $17.47, Lyft $15.47 | Base is within 2% of Waymo's average and 14% above Uber's; low case equals Lyft | **Modestly aggressive**: assumes a robotaxi price premium over mainstream ride-hail. One city, one operator, not a national average |
| **Operating cost per mile $1.50 / $1.10 / $0.80** (excludes depreciation and charging). Our all-in opex is $1.15-1.22 per total mile once charging is added | AAA Your Driving Costs 2025 (opened): private-car maintenance 11.04 cents per mile, full-coverage insurance $1,694 a year, about 11 cents per mile at 15,000 miles. SoftwareSeni article citing Sacra: Waymo about $1.40 per mile all-in and Tesla about $0.81; Goldman Sachs depreciation 35 cents falling to 14 cents per mile | Against private-car components (about 22 cents) ours is five times higher, but ours also covers remote assistance, cleaning, depot and platform fees that AAA excludes. If Waymo's $1.40 includes about 35 cents of depreciation, its operating cost is about $1.05, slightly below ours | **Neutral to conservative**, low confidence: the robotaxi figures are secondary-source company estimates. A Benzinga analyst estimate (about $1 per mile including depreciation) could not be opened (HTTP 403) and is not used |
| **Deadhead share 50% / 40% / 30%** and **trips per vehicle per day 12 / 18 / 25** | Same SoftwareSeni article: 43-45% of Waymo's California miles carry no passenger (CPUC VMT reporting, as cited); Waymo vehicles on Uber reach 25-30 trips a day (Platform Aeronaut, as cited) | Deadhead base is 3-5 points below the reported share (the 50% low case covers it); trips per day base is well below the reported 25-30 | Deadhead **slightly aggressive**; utilization **conservative**. Both from secondary citations |
| **Vehicle cost $200k / $140k / $100k** | Morgan Stanley estimates via TheNextWeb (opened): Jaguar I-PACE about $200,000 per unit, Zeekr-built Ojai about $125,000, next-generation driver hardware under $20,000 | Base is 30% below the current-generation estimate and 12% above the next-generation one; our low case equals the Jaguar estimate | **Mid-range**: aggressive for a current-generation fleet, conservative for the next generation |

Sensitivity worth knowing (simple division from the base case, not a pipeline run): with a $200k vehicle and every other input at base, San Francisco payback is about 3.5 years instead of 2.4 (contribution $57,846 a year). Payback therefore stays assumption-driven, as the deck states.

## What to fix before sharing

In priority order. None of these were changed here.

1. **Update Waymo in Chicago to `testing`.** It is a confirmed change, and it re-orders ranks 4 to 9 (see section 6). The memo, deck, README and app all quote Chicago at #4, and Phoenix is currently described as borderline (50.4% confidence), so those would need regenerating.
2. **Say that ranks 4 to 10 are tie-sensitive.** Because crowding has few distinct values, one competitor-status change can move a metro five places. A line in the memo's confidence section and in `docs/methodology.md` would pre-empt the question. The alternative is a finer crowding measure.
3. **Fix two citations.** Replace New York's regulation source with a page that states the one-hand rule (Cleantechnica 2026-02-20 was readable). Replace Pennsylvania's tier source with a readable page (the PennDOT page returned no body text).
4. **Disclose the weather level bias.** State in `docs/methodology.md` that the Open-Meteo archive runs high on rain days (20-49% vs NOAA stations in this check) and low on 40 C+ days (10-22%). The ranking is robust to this, but a reader comparing "Phoenix: 25 rain days" to NOAA's 16.5 will see a mismatch.
5. **Put public references into `assumptions.yaml`.** Fare (Obi), vehicle cost (Morgan Stanley) and AAA/Sacra for cost per mile give those inputs a `source_url` instead of "analyst assumption". Note the fare is a premium assumption.
6. **Two minor items.** Michigan's Tier 2 versus 3 is a judgment call worth a note. Several competitor sources are four to twelve months old (Nuro-Lucid Oct 2025, Zoox Atlanta May 2025, Tesla Phoenix Jul 2026); they re-confirmed today but will age.

Not validated: the Monte Carlo and demand-index methods were not checked against an external source, because there is no published ground truth for them. The NYC 2025 annual total is the only item where a source was looked for and not found.
