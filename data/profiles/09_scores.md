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
| total | 40.06 | 52.75 | 63.21 |
| demand | 11.9 | 50.3 | 91.7 |
| operating | 20.4 | 47.5 | 85.4 |
| regulatory | 13.3 | 52.1 | 75.4 |
| competition | 0 | 66.7 | 90 |
| charging | 6.2 | 52.1 | 93.8 |

## Sample rows
| metro             |   total |   demand |   operating |   regulatory |   competition |   charging |
|:------------------|--------:|---------:|------------:|-------------:|--------------:|-----------:|
| New York          |   57.85 |     91.7 |        35.4 |         13.3 |          86.7 |       25   |
| Los Angeles       |   60.9  |     63.3 |        80   |         52.1 |          53.3 |        6.2 |
| Chicago           |   55.61 |     82.3 |        37.9 |         13.3 |          86.7 |       33.3 |
| Dallas-Fort Worth |   49.44 |     50.8 |        47.5 |         75.4 |           0   |       93.8 |
| Houston           |   56.2  |     53.1 |        53.3 |         75.4 |          30   |       93.8 |

## Sanity checks
- [PASS] scores within 0-100
- [PASS] all scenario weight sets sum to 100
- [PASS] sub-metric weights sum to 100 per pillar
- [PASS] 25 candidates ranked in each scenario, Vegas unranked
- [PASS] Phoenix or San Diego above Minneapolis on operating pillar

### Top 10: balanced {'demand': 35, 'operating': 25, 'regulatory': 20, 'competition': 15, 'charging': 5}
| metro         |   balanced |   total |
|:--------------|-----------:|--------:|
| Miami         |          1 |    63.2 |
| Los Angeles   |          2 |    60.9 |
| Phoenix       |          3 |    58.2 |
| New York      |          4 |    57.9 |
| San Francisco |          5 |    57.7 |
| Houston       |          6 |    56.2 |
| Tampa         |          7 |    56.1 |
| Chicago       |          8 |    55.6 |
| Orlando       |          9 |    55.1 |
| Atlanta       |         10 |    55.1 |

### Top 10: fast_growth {'demand': 50, 'operating': 20, 'regulatory': 15, 'competition': 10, 'charging': 5}
| metro         |   fast_growth |   total |
|:--------------|--------------:|--------:|
| Miami         |             1 |    67.1 |
| New York      |             2 |    64.8 |
| San Francisco |             3 |    62.2 |
| Los Angeles   |             4 |    61.1 |
| Chicago       |             5 |    61.1 |
| Washington DC |             6 |    57.7 |
| Philadelphia  |             7 |    57.1 |
| Atlanta       |             8 |    56.7 |
| Houston       |             9 |    56.2 |
| Boston        |            10 |    55.5 |

### Top 10: low_risk {'demand': 20, 'operating': 35, 'regulatory': 30, 'competition': 10, 'charging': 5}
| metro         |   low_risk |   total |
|:--------------|-----------:|--------:|
| Phoenix       |          1 |    64.7 |
| Miami         |          2 |    62.6 |
| Tampa         |          3 |    62.4 |
| Los Angeles   |          4 |    61.9 |
| Orlando       |          5 |    61.1 |
| Houston       |          6 |    59.6 |
| San Francisco |          7 |    57.8 |
| San Diego     |          8 |    57.7 |
| San Antonio   |          9 |    57.6 |
| Atlanta       |         10 |    56.5 |

### Top 10: capital_light {'demand': 25, 'operating': 25, 'regulatory': 20, 'competition': 20, 'charging': 10}
| metro        |   capital_light |   total |
|:-------------|----------------:|--------:|
| Miami        |               1 |    60.7 |
| Phoenix      |               2 |    60.2 |
| Tampa        |               3 |    59.2 |
| Orlando      |               4 |    58.3 |
| Los Angeles  |               5 |    57.5 |
| Houston      |               6 |    57.1 |
| San Antonio  |               7 |    56.8 |
| New York     |               8 |    54.3 |
| Philadelphia |               9 |    53.8 |
| Atlanta      |              10 |    53.6 |

### Movement between scenarios (max rank - min rank)
| metro         |   balanced |   fast_growth |   low_risk |   capital_light |   rank_range |
|:--------------|-----------:|--------------:|-----------:|----------------:|-------------:|
| New York      |          4 |             2 |         19 |               8 |           17 |
| Chicago       |          8 |             5 |         20 |              11 |           15 |
| Washington DC |         13 |             6 |         21 |              18 |           15 |
| Boston        |         17 |            10 |         24 |              21 |           14 |
| San Antonio   |         16 |            20 |          9 |               7 |           13 |
| San Francisco |          5 |             3 |          7 |              15 |           12 |
| San Diego     |         15 |            19 |          8 |              14 |           11 |
| Austin        |         23 |            24 |         13 |              23 |           11 |
| Orlando       |          9 |            15 |          5 |               4 |           11 |
| Tampa         |          7 |            13 |          3 |               3 |           10 |
| Philadelphia  |         11 |             7 |         17 |               9 |           10 |
| Phoenix       |          3 |            11 |          1 |               2 |           10 |

### Vegas benchmark (not ranked)
Total 54.2; pillars {"demand": 35.8, "operating": 71.7, "regulatory": 63.7, "competition": 43.3, "charging": 89.8}

### Most / least similar to Vegas
| metro             |   sim |
|:------------------|------:|
| Phoenix           |  56.3 |
| Dallas-Fort Worth |  38.4 |
| Austin            |  34.1 |
| Denver            |  33.4 |
| Orlando           |  32.9 |
| metro      |   sim |
|:-----------|------:|
| New York   |   0   |
| Pittsburgh |   1.5 |
| Detroit    |  12.1 |