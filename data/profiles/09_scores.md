# Profile: 09_scores
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| total | float64 | 0 |
| demand | float64 | 0 |
| operating | float64 | 0 |
| regulatory | float64 | 0 |
| competition | float64 | 0 |
| charging | float64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| total | 37.07 | 49.95 | 63.98 |
| demand | 11.9 | 50.3 | 91.7 |
| operating | 28.8 | 47.7 | 85.4 |
| regulatory | 8.3 | 72.9 | 72.9 |
| competition | 0 | 47.9 | 85.4 |
| charging | 6.2 | 52.1 | 93.8 |

## Sample rows
| metro             |   total |   demand |   operating |   regulatory |   competition |   charging |
|:------------------|--------:|---------:|------------:|-------------:|--------------:|-----------:|
| New York          |   51.98 |     91.7 |        30.4 |          8.3 |          62.5 |       25   |
| Los Angeles       |   59.56 |     63.3 |        77.5 |         72.9 |          20.8 |        6.2 |
| Chicago           |   53.8  |     82.3 |        35.4 |          8.3 |          85.4 |       33.3 |
| Dallas-Fort Worth |   48.73 |     50.8 |        46.7 |         72.9 |           0   |       93.8 |
| Houston           |   49.84 |     53.1 |        35.4 |         72.9 |          20.8 |       93.8 |

## Sanity checks
- [PASS] scores within 0-100
- [PASS] all scenario weight sets sum to 100
- [PASS] sub-metric weights sum to 100 per pillar
- [PASS] 25 candidates ranked in each scenario, Vegas unranked
- [PASS] Phoenix or San Diego above Minneapolis on operating pillar

### Top 10: balanced {'demand': 35, 'operating': 25, 'regulatory': 20, 'competition': 15, 'charging': 5}
| metro         |   balanced |   total |
|:--------------|-----------:|--------:|
| San Francisco |          1 |    64   |
| Los Angeles   |          2 |    59.6 |
| Miami         |          3 |    59   |
| Philadelphia  |          4 |    55.7 |
| Atlanta       |          5 |    53.8 |
| Phoenix       |          5 |    53.8 |
| Chicago       |          7 |    53.8 |
| Washington DC |          8 |    53.2 |
| San Diego     |          9 |    52.6 |
| New York      |         10 |    52   |

### Top 10: fast_growth {'demand': 50, 'operating': 20, 'regulatory': 15, 'competition': 10, 'charging': 5}
| metro         |   fast_growth |   total |
|:--------------|--------------:|--------:|
| San Francisco |             1 |    67   |
| Miami         |             2 |    64.2 |
| New York      |             3 |    60.7 |
| Los Angeles   |             4 |    60.5 |
| Chicago       |             5 |    59.7 |
| Philadelphia  |             6 |    58.1 |
| Washington DC |             6 |    58.1 |
| Atlanta       |             8 |    55.9 |
| Boston        |             9 |    54.9 |
| Detroit       |            10 |    52.4 |

### Top 10: low_risk {'demand': 20, 'operating': 35, 'regulatory': 30, 'competition': 10, 'charging': 5}
| metro         |   low_risk |   total |
|:--------------|-----------:|--------:|
| San Francisco |          1 |    67.4 |
| Los Angeles   |          2 |    64.1 |
| San Diego     |          3 |    62.1 |
| Phoenix       |          4 |    61.5 |
| Miami         |          5 |    59.1 |
| Sacramento    |          6 |    56.1 |
| Atlanta       |          7 |    55.7 |
| Tampa         |          8 |    55.4 |
| San Antonio   |          9 |    55.1 |
| Orlando       |         10 |    53.6 |

### Top 10: capital_light {'demand': 25, 'operating': 25, 'regulatory': 20, 'competition': 20, 'charging': 10}
| metro         |   capital_light |   total |
|:--------------|----------------:|--------:|
| San Francisco |               1 |    57.3 |
| Miami         |               2 |    55.4 |
| Philadelphia  |               3 |    55.1 |
| Los Angeles   |               4 |    54.6 |
| Phoenix       |               5 |    54.4 |
| San Diego     |               6 |    52.7 |
| San Antonio   |               6 |    52.7 |
| Sacramento    |               8 |    52.6 |
| Atlanta       |               9 |    51.9 |
| Seattle       |              10 |    51.7 |

### Movement between scenarios (max rank - min rank)
| metro         |   balanced |   fast_growth |   low_risk |   capital_light |   rank_range |
|:--------------|-----------:|--------------:|-----------:|----------------:|-------------:|
| New York      |         10 |             3 |         23 |              19 |           20 |
| Chicago       |          7 |             5 |         21 |              12 |           16 |
| San Antonio   |         19 |            21 |          9 |               6 |           15 |
| Sacramento    |         12 |            20 |          6 |               8 |           14 |
| Washington DC |          8 |             6 |         20 |              14 |           14 |
| San Diego     |          9 |            16 |          3 |               6 |           13 |
| Boston        |         16 |             9 |         22 |              20 |           13 |
| Philadelphia  |          4 |             6 |         14 |               3 |           11 |
| Austin        |         24 |            24 |         13 |              24 |           11 |
| Nashville     |         25 |            25 |         17 |              25 |            8 |
| Orlando       |         18 |            18 |         10 |              16 |            8 |
| Minneapolis   |         20 |            17 |         25 |              22 |            8 |

### Vegas benchmark (not ranked)
Total 50.6; pillars {"demand": 35.8, "operating": 68.6, "regulatory": 72.9, "competition": 12.5, "charging": 89.8}

### Most / least similar to Vegas
| metro             |   sim |
|:------------------|------:|
| Phoenix           |  61.9 |
| Sacramento        |  35.5 |
| Charlotte         |  32.4 |
| Dallas-Fort Worth |  31.6 |
| Los Angeles       |  30.2 |
| metro        |   sim |
|:-------------|------:|
| New York     |   0   |
| Pittsburgh   |   6.4 |
| Philadelphia |  13   |