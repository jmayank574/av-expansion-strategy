# Profile: 07_seed_and_crosscheck
rows: 42

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
| metro         | competitor   | status           | first_public_date   | platform_partner   | source_url         | source_title              | as_of_date   | confidence   |
|:--------------|:-------------|:-----------------|:--------------------|:-------------------|:-------------------|:--------------------------|:-------------|:-------------|
| Atlanta       | Waymo        | operating_public |                     | Uber               | https://waymo.com/ | Waymo - Serving Riders In | 2026-11-05   | high         |
| Austin        | Waymo        | operating_public |                     | Uber               | https://waymo.com/ | Waymo - Serving Riders In | 2026-11-05   | high         |
| Los Angeles   | Waymo        | operating_public |                     |                    | https://waymo.com/ | Waymo - Serving Riders In | 2026-11-05   | high         |
| Phoenix       | Waymo        | operating_public |                     |                    | https://waymo.com/ | Waymo - Serving Riders In | 2026-11-05   | high         |
| San Francisco | Waymo        | operating_public |                     |                    | https://waymo.com/ | Waymo - Serving Riders In | 2026-11-05   | high         |

## Sanity checks
- [PASS] regulation covers every state of the 26 metros
- [PASS] regulation: one row per state
- [PASS] regulation: tier in 0-3
- [PASS] regulation: source fields filled
- [PASS] regulation: confidence values valid
- [PASS] competitors: metro names all in metros.yaml
- [PASS] competitors: status values valid
- [PASS] competitors: source fields filled
- [PASS] competitors: no duplicate (metro, competitor)

## Cross-check: seed competitor_presence vs NHTSA ADS incidents (24 months, operators with >= 5 incidents in the metro)
| metro             | seed_active          | seed_announced         | nhtsa_active                                         | nhtsa_not_in_seed   | announced_without_nhtsa   |
|:------------------|:---------------------|:-----------------------|:-----------------------------------------------------|:--------------------|:--------------------------|
| Atlanta           | Waymo, Zoox          | -                      | May Mobility (13), Waymo (77)                        | May Mobility        | -                         |
| Austin            | Tesla, Waymo, Zoox   | -                      | Avride (29), Tesla (26), Waymo (181), Zoox (5)       | Avride              | -                         |
| Boston            | Waymo                | -                      | -                                                    | -                   | -                         |
| Charlotte         | -                    | Waymo                  | -                                                    | -                   | Waymo                     |
| Chicago           | -                    | Waymo                  | -                                                    | -                   | Waymo                     |
| Dallas-Fort Worth | Avride, Tesla, Waymo | Lyft/Mobileye/Marubeni | Avride (54), May Mobility (8), Tesla (7), Waymo (14) | May Mobility        | Lyft/Mobileye/Marubeni    |
| Denver            | Waymo                | -                      | -                                                    | -                   | -                         |
| Detroit           | -                    | Waymo                  | -                                                    | -                   | -                         |
| Houston           | Tesla, Waymo         | -                      | Nuro (5), Waymo (18)                                 | Nuro                | -                         |
| Las Vegas         | Waymo, Zoox          | Tesla                  | Motional (20), Zoox (46)                             | Motional            | Tesla                     |
| Los Angeles       | Waymo, Zoox          | -                      | Waymo (462)                                          | -                   | -                         |
| Miami             | Tesla, Waymo, Zoox   | -                      | Waymo (25), Zoox (6)                                 | -                   | -                         |
| Minneapolis       | Waymo                | -                      | -                                                    | -                   | -                         |
| Nashville         | Waymo                | -                      | Waymo (10)                                           | -                   | -                         |
| New York          | Waymo                | -                      | -                                                    | -                   | -                         |
| Orlando           | Waymo                | Tesla                  | Waymo (9)                                            | -                   | Tesla                     |
| Philadelphia      | -                    | Waymo                  | Waymo (5)                                            | -                   | -                         |
| Phoenix           | Waymo                | Tesla                  | Waymo (338)                                          | -                   | Tesla                     |
| Pittsburgh        | -                    | Waymo                  | -                                                    | -                   | Waymo                     |
| Sacramento        | -                    | Waymo                  | -                                                    | -                   | Waymo                     |
| San Antonio       | Waymo                | -                      | Waymo (5)                                            | -                   | -                         |
| San Diego         | Waymo                | -                      | -                                                    | -                   | -                         |
| San Francisco     | Waymo, Zoox          | -                      | Waymo (691), Zoox (49)                               | -                   | -                         |
| Seattle           | -                    | Waymo                  | -                                                    | -                   | Waymo                     |
| Tampa             | Waymo                | Tesla                  | -                                                    | -                   | -                         |
| Washington DC     | -                    | Waymo                  | Waymo (6)                                            | -                   | -                         |

### Flag A: NHTSA shows activity the seed file lacks
| metro             | nhtsa_not_in_seed   | nhtsa_active                                         |
|:------------------|:--------------------|:-----------------------------------------------------|
| Atlanta           | May Mobility        | May Mobility (13), Waymo (77)                        |
| Austin            | Avride              | Avride (29), Tesla (26), Waymo (181), Zoox (5)       |
| Dallas-Fort Worth | May Mobility        | Avride (54), May Mobility (8), Tesla (7), Waymo (14) |
| Houston           | Nuro                | Nuro (5), Waymo (18)                                 |
| Las Vegas         | Motional            | Motional (20), Zoox (46)                             |

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
| file        | item                 | confidence   | source_title                                               |
|:------------|:---------------------|:-------------|:-----------------------------------------------------------|
| competitors | San Francisco / Zoox | low          | Zoox - Where to Ride (page lists city but gives no status) |
| competitors | Austin / Zoox        | low          | Zoox - Where to Ride (page lists city but gives no status) |
| competitors | Miami / Zoox         | low          | Zoox - Where to Ride (page lists city but gives no status) |
| competitors | Atlanta / Zoox       | low          | Zoox - Where to Ride (page lists city but gives no status) |
| competitors | Los Angeles / Zoox   | low          | Zoox - Where to Ride (page lists city but gives no status) |
| competitors | Las Vegas / Zoox     | low          | Zoox - Where to Ride (page lists city but gives no status) |

### Dropped rows (could not verify from an opened source)
- competitor_presence: Nuro/Lucid (San Francisco, announced) and May Mobility/Lyft (Atlanta, announced). The only pages found were search results that I did not open.
- Waymo city-level 'operating_limited' vs 'operating_public' for Dallas, Houston, Miami, Nashville, Orlando, San Antonio is my judgment from search extracts: waymo.com does not state access tiers.
- Platform partners were recorded only where an opened page stated them (Waymo on Uber in Atlanta and Austin).
- Tesla rows rest on a fan/news site rather than Tesla filings.