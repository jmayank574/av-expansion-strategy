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
| total | 37.26 | 49.44 | 60.79 |
| demand | 11.9 | 50.3 | 91.7 |
| operating | 28.8 | 47.7 | 85.4 |
| regulatory | 13.3 | 52.1 | 75.4 |
| competition | 0 | 45.8 | 91.7 |
| charging | 6.2 | 52.1 | 93.8 |

## Sample rows
| metro             |   total |   demand |   operating |   regulatory |   competition |   charging |
|:------------------|--------:|---------:|------------:|-------------:|--------------:|-----------:|
| New York          |   54.54 |     91.7 |        30.4 |         13.3 |          72.9 |       25   |
| Los Angeles       |   56.02 |     63.3 |        77.5 |         52.1 |          25   |        6.2 |
| Chicago           |   55.74 |     82.3 |        35.4 |         13.3 |          91.7 |       33.3 |
| Dallas-Fort Worth |   49.23 |     50.8 |        46.7 |         75.4 |           0   |       93.8 |
| Houston           |   49.72 |     53.1 |        35.4 |         75.4 |          16.7 |       93.8 |

## Sanity checks
- [PASS] scores within 0-100
- [PASS] all scenario weight sets sum to 100
- [PASS] sub-metric weights sum to 100 per pillar
- [PASS] 25 candidates ranked in each scenario, Vegas unranked
- [PASS] Phoenix or San Diego above Minneapolis on operating pillar

### Top 10: balanced {'demand': 35, 'operating': 25, 'regulatory': 20, 'competition': 15, 'charging': 5}
| metro         |   balanced |   total |
|:--------------|-----------:|--------:|
| Miami         |          1 |    60.8 |
| San Francisco |          2 |    58.9 |
| Los Angeles   |          3 |    56   |
| Chicago       |          4 |    55.7 |
| Phoenix       |          5 |    54.9 |
| New York      |          6 |    54.5 |
| Detroit       |          7 |    53.8 |
| Atlanta       |          8 |    53.7 |
| Philadelphia  |          9 |    53   |
| Boston        |         10 |    51.6 |

### Top 10: fast_growth {'demand': 50, 'operating': 20, 'regulatory': 15, 'competition': 10, 'charging': 5}
| metro         |   fast_growth |   total |
|:--------------|--------------:|--------:|
| Miami         |             1 |    65.4 |
| San Francisco |             2 |    63.3 |
| New York      |             3 |    62.5 |
| Chicago       |             4 |    61.1 |
| Los Angeles   |             5 |    57.8 |
| Boston        |             6 |    56.7 |
| Philadelphia  |             7 |    56.2 |
| Washington DC |             8 |    56.1 |
| Atlanta       |             9 |    55.8 |
| Detroit       |            10 |    54.1 |

### Top 10: low_risk {'demand': 20, 'operating': 35, 'regulatory': 30, 'competition': 10, 'charging': 5}
| metro             |   low_risk |   total |
|:------------------|-----------:|--------:|
| Phoenix           |          1 |    62.7 |
| Miami             |          2 |    60.7 |
| San Francisco     |          3 |    60.5 |
| Los Angeles       |          4 |    58.2 |
| Atlanta           |          5 |    56   |
| Tampa             |          6 |    55.9 |
| San Antonio       |          7 |    55.7 |
| San Diego         |          8 |    55.6 |
| Orlando           |          9 |    54.1 |
| Dallas-Fort Worth |         10 |    53.8 |

### Top 10: capital_light {'demand': 25, 'operating': 25, 'regulatory': 20, 'competition': 20, 'charging': 10}
| metro         |   capital_light |   total |
|:--------------|----------------:|--------:|
| Miami         |               1 |    57.6 |
| Phoenix       |               2 |    55.8 |
| Detroit       |               3 |    53.9 |
| Chicago       |               4 |    53.8 |
| San Antonio   |               5 |    52.7 |
| Charlotte     |               6 |    52.1 |
| San Francisco |               7 |    51.9 |
| Philadelphia  |               8 |    51.7 |
| Tampa         |               9 |    51.6 |
| Atlanta       |              10 |    51.6 |

### Movement between scenarios (max rank - min rank)
| metro         |   balanced |   fast_growth |   low_risk |   capital_light |   rank_range |
|:--------------|-----------:|--------------:|-----------:|----------------:|-------------:|
| New York      |          6 |             3 |         22 |              13 |           19 |
| Chicago       |          4 |             4 |         20 |               4 |           16 |
| Charlotte     |         22 |            22 |         16 |               6 |           16 |
| Boston        |         10 |             6 |         21 |              18 |           15 |
| Washington DC |         11 |             8 |         23 |              22 |           15 |
| San Antonio   |         18 |            20 |          7 |               5 |           15 |
| Detroit       |          7 |            10 |         15 |               3 |           12 |
| Austin        |         24 |            24 |         12 |              24 |           12 |
| San Diego     |         17 |            19 |          8 |              19 |           11 |
| Tampa         |         13 |            17 |          6 |               9 |           11 |
| Sacramento    |         19 |            23 |         13 |              16 |           10 |
| Phoenix       |          5 |            11 |          1 |               2 |           10 |

### Vegas benchmark (not ranked)
Total 48.2; pillars {"demand": 35.8, "operating": 68.6, "regulatory": 63.7, "competition": 8.9, "charging": 89.8}

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