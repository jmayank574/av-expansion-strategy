# Profile: 07_seed_and_crosscheck
rows: 51

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| competitor | str | 0 |
| status | str | 0 |
| first_public_date | str | 0 |
| platform_partner | str | 0 |
| source_url | str | 0 |
| source_title | str | 0 |
| as_of_date | str | 0 |
| confidence | str | 0 |

## Sample rows
| metro   | competitor   | status            | first_public_date   | platform_partner   | source_url                                                                                  | source_title                                                                                                                       | as_of_date   | confidence   |
|:--------|:-------------|:------------------|:--------------------|:-------------------|:--------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|:-------------|:-------------|
| Atlanta | May Mobility | operating_limited | 2025-09             | Lyft               | https://www.sec.gov/Archives/edgar/data/0002111542/000121390026100367/ea030470201ex99-2.htm | May Mobility investor presentation (SEC Form 8-K exhibit, 2026), slide 17                                                          | 2026-05-29   | medium       |
| Atlanta | Waymo        | operating_public  |                     | Uber               | https://waymo.com/whereyoucango/                                                            | Waymo - Where you can go (undated page, opened 2026-11-06)                                                                         | 2026-11-06   | medium       |
| Atlanta | Zoox         | testing           |                     |                    | https://www.insurancejournal.com/news/southeast/2025/05/21/824605.htm                       | Insurance Journal: Zoox testing in Atlanta (safety drivers, mapping); Electrek 2026-03-24 lists Atlanta as being mapped and tested | 2025-05-21   | medium       |
| Austin  | Avride       | testing           |                     |                    | https://en.wikipedia.org/wiki/Avride                                                        | Wikipedia: Avride (secondary source) lists Austin as on-road testing; paid robotaxi is Dallas only                                 | 2026-11-06   | medium       |
| Austin  | Tesla        | operating_limited |                     |                    | https://electrek.co/2026/04/30/tesla-robotaxi-unsupervised-finally-signs-ramping-up/        | Electrek: Tesla Robotaxi unsupervised fleet (Austin 19, Dallas 3, Houston 3 vehicles)                                              | 2026-04-30   | high         |

## Sanity checks
- [PASS] regulation covers every state of the 26 metros
- [PASS] regulation: one row per state
- [PASS] regulation: tier in 0-3
- [PASS] regulation: source fields filled
- [PASS] regulation: confidence values valid
- [PASS] regulation: new_entrant_path is fast | moderate | slow
- [PASS] regulation: new-entrant source fields filled
- [PASS] regulation: new-entrant confidence values valid
- [PASS] competitors: metro names all in metros.yaml
- [PASS] competitors: status values valid
- [PASS] competitors: source fields filled
- [PASS] competitors: no duplicate (metro, competitor)

## Cross-check: seed competitor_presence vs NHTSA ADS incidents (24 months, operators with >= 5 incidents in the metro)
| metro             | seed_active                | seed_announced                       | nhtsa_active                                         | nhtsa_not_in_seed   | announced_without_nhtsa   |
|:------------------|:---------------------------|:-------------------------------------|:-----------------------------------------------------|:--------------------|:--------------------------|
| Atlanta           | May Mobility, Waymo, Zoox  | -                                    | May Mobility (13), Waymo (77)                        | -                   | -                         |
| Austin            | Avride, Tesla, Waymo, Zoox | -                                    | Avride (29), Tesla (26), Waymo (181), Zoox (5)       | -                   | -                         |
| Boston            | Waymo                      | -                                    | -                                                    | -                   | -                         |
| Charlotte         | -                          | Waymo                                | -                                                    | -                   | Waymo                     |
| Chicago           | -                          | Waymo                                | -                                                    | -                   | Waymo                     |
| Dallas-Fort Worth | Avride, Tesla, Waymo       | Lyft/Mobileye/Marubeni, May Mobility | Avride (54), May Mobility (8), Tesla (7), Waymo (14) | -                   | Lyft/Mobileye/Marubeni    |
| Denver            | Waymo                      | -                                    | -                                                    | -                   | -                         |
| Detroit           | -                          | Waymo                                | -                                                    | -                   | -                         |
| Houston           | Nuro, Tesla, Waymo         | -                                    | Nuro (5), Waymo (18)                                 | -                   | -                         |
| Las Vegas         | Motional, Waymo, Zoox      | Tesla                                | Motional (20), Zoox (46)                             | -                   | Tesla                     |
| Los Angeles       | Waymo, Zoox                | -                                    | Waymo (462)                                          | -                   | -                         |
| Miami             | Tesla, Waymo, Zoox         | -                                    | Waymo (25), Zoox (6)                                 | -                   | -                         |
| Minneapolis       | Waymo                      | -                                    | -                                                    | -                   | -                         |
| Nashville         | Waymo                      | -                                    | Waymo (10)                                           | -                   | -                         |
| New York          | Waymo                      | -                                    | -                                                    | -                   | -                         |
| Orlando           | Waymo                      | Tesla                                | Waymo (9)                                            | -                   | Tesla                     |
| Philadelphia      | Waymo                      | -                                    | Waymo (5)                                            | -                   | -                         |
| Phoenix           | Waymo                      | Tesla                                | Waymo (338)                                          | -                   | Tesla                     |
| Pittsburgh        | -                          | Waymo                                | -                                                    | -                   | Waymo                     |
| Sacramento        | -                          | Waymo                                | -                                                    | -                   | Waymo                     |
| San Antonio       | Waymo                      | -                                    | Waymo (5)                                            | -                   | -                         |
| San Diego         | Waymo                      | -                                    | -                                                    | -                   | -                         |
| San Francisco     | Nuro, Tesla, Waymo, Zoox   | -                                    | Waymo (691), Zoox (49)                               | -                   | -                         |
| Seattle           | Zoox                       | Waymo                                | -                                                    | -                   | Waymo                     |
| Tampa             | Waymo                      | Tesla                                | -                                                    | -                   | -                         |
| Washington DC     | Zoox                       | Waymo                                | Waymo (6)                                            | -                   | -                         |

### Flag A: NHTSA shows activity the seed file lacks
none

### Flag B: announced in seed but no NHTSA activity (expected for cities not yet launched)
| metro             | announced_without_nhtsa   |
|:------------------|:--------------------------|
| Charlotte         | Waymo                     |
| Chicago           | Waymo                     |
| Dallas-Fort Worth | Lyft/Mobileye/Marubeni    |
| Las Vegas         | Tesla                     |
| Orlando           | Tesla                     |
| Phoenix           | Tesla                     |
| Pittsburgh        | Waymo                     |
| Sacramento        | Waymo                     |
| Seattle           | Waymo                     |

## Needs human review (low-confidence rows; sources not opened or status not stated)
| file        | item                 | confidence   | source_title                                                                         |
|:------------|:---------------------|:-------------|:-------------------------------------------------------------------------------------|
| competitors | Washington DC / Zoox | low          | TechCrunch: Zoox's next testbed is Washington DC (also lists Seattle as a test site) |

### Rows researched on 2026-11-06 and notes
- All 26 metros have at least one sourced row. Every status comes from a page opened during the research (company pages, TechCrunch, Electrek, Insurance Journal, PhillyVoice, an SEC investor deck).
- Waymo access tiers: operating_public = waymo.com/whereyoucango says anyone can ride, or press reports of the waitlist ending; Denver and Las Vegas are 'gradually adding riders' = operating_limited. The waymo.com page is undated and lags press reports for Houston and San Antonio, so those two cite the press report and are medium confidence.
- Tesla rows rest partly on a fan site (Miami launch, upcoming-city list); Austin, Dallas, Houston and the Bay Area rest on Electrek. Tesla Orlando and Tampa: one search result claimed unsupervised rides began there but no opened source confirms it, so they stay 'announced'.
- Zoox: Atlanta and Los Angeles are 'testing' (mapping/testing, no public rides) per Electrek 2026-03-24. Washington DC is low confidence: the source (2025-09-30) describes mapping with safety drivers and planned autonomous testing; no newer source found.
- Avride Austin rests on a Wikipedia page (secondary source), medium confidence; it is consistent with NHTSA showing 29 Avride incidents in Austin.
- Not included (could not verify from an opened source as current): May Mobility Detroit (a 2024 pilot for select residents, run through 2026), Motional Pittsburgh, Tesla Orlando/Tampa as operating.
- Platform partners were recorded only where an opened page stated them.
- Waymo Washington DC stays 'announced' (waymo.com Up Next) although NHTSA shows 6 Waymo incidents there, so some testing is likely. Not changed because no opened source states it.