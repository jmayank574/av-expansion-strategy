# Profile: 02_gazetteer
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| place_geoid | str | 0 |
| land_sqmi | float64 | 0 |
| city_pop | float64 | 0 |
| density_per_sqmi | float64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| land_sqmi | 36 | 140.3 | 640.8 |
| city_pop | 3.048e+05 | 7.365e+05 | 8.484e+06 |
| density_per_sqmi | 1,451 | 4,676 | 2.823e+04 |

## Sample rows
| metro             |   place_geoid |   land_sqmi |    city_pop |   density_per_sqmi |
|:------------------|--------------:|------------:|------------:|-------------------:|
| New York          |       3651000 |     300.483 | 8.48384e+06 |           28234    |
| Los Angeles       |       0644000 |     470.518 | 3.85726e+06 |            8197.91 |
| Chicago           |       1714000 |     227.748 | 2.71123e+06 |           11904.5  |
| Dallas-Fort Worth |       4819000 |     339.685 | 1.30793e+06 |            3850.42 |
| Houston           |       4835000 |     640.819 | 2.32825e+06 |            3633.25 |

## Sanity checks
- [PASS] all 26 present, no null area
- [PASS] NYC has highest density
- [PASS] SF, Boston or Chicago in positions 2-4

Top 5 density: New York, San Francisco, Boston, Miami, Chicago