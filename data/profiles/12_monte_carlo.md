# Profile: 12_monte_carlo
rows: 25

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| top_n_share | float64 | 0 |
| median_rank | float64 | 0 |
| p10_rank | float64 | 0 |
| p90_rank | float64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| top_n_share | 0 | 0.0249 | 0.9505 |
| median_rank | 1 | 13 | 25 |
| p10_rank | 1 | 7 | 24 |
| p90_rank | 4 | 20 | 25 |

## Sample rows
| metro             |   top_n_share |   median_rank |   p10_rank |   p90_rank |
|:------------------|--------------:|--------------:|-----------:|-----------:|
| New York          |        0.473  |             6 |          3 |         16 |
| Los Angeles       |        0.6319 |             5 |          3 |          9 |
| Chicago           |        0.6176 |             4 |          1 |         12 |
| Dallas-Fort Worth |        0.0249 |            13 |          7 |         22 |
| Houston           |        0.0348 |            13 |          7 |         20 |

## Sanity checks
- [PASS] reproducible: two runs with the same seed are identical
- [PASS] top-5 shares sum to 5 (five metros in each draw, barring ties)
- [PASS] mean drawn weights are within 1 point of the balanced weights
- [PASS] every deterministic top-5 metro is in the top 10 by Monte Carlo share

10,000 Dirichlet draws, seed 42, concentration 50 around the balanced weights {'demand': 35, 'operating': 25, 'regulatory': 20, 'competition': 15, 'charging': 5}.
Mean drawn weights: demand 35.0, operating 25.0, regulatory 20.0, competition 15.0, charging 4.9; std: demand 6.7, operating 6.1, regulatory 5.7, competition 5.0, charging 3.0

## Share of draws in the top 5 and median rank
| metro             |   top5_share |   median_rank |   p10_rank |   p90_rank |   deterministic_rank |
|:------------------|-------------:|--------------:|-----------:|-----------:|---------------------:|
| Miami             |         95   |             1 |          1 |          4 |                    1 |
| San Francisco     |         85.4 |             2 |          1 |          7 |                    2 |
| Los Angeles       |         63.2 |             5 |          3 |          9 |                    3 |
| Chicago           |         61.8 |             4 |          1 |         12 |                    4 |
| Phoenix           |         50.6 |             5 |          2 |         11 |                    5 |
| New York          |         47.3 |             6 |          3 |         16 |                    6 |
| Atlanta           |         36.2 |             7 |          4 |         12 |                    8 |
| Detroit           |         26.9 |             7 |          3 |         12 |                    7 |
| Philadelphia      |         10.9 |             8 |          5 |         13 |                    9 |
| Boston            |          6.2 |            10 |          6 |         18 |                   10 |
| San Diego         |          4.2 |            16 |          8 |         22 |                   17 |
| Houston           |          3.5 |            13 |          7 |         20 |                   12 |
| Dallas-Fort Worth |          2.5 |            13 |          7 |         22 |                   14 |
| San Antonio       |          2.2 |            18 |          9 |         22 |                   18 |
| Sacramento        |          2   |            19 |         10 |         22 |                   19 |
| Tampa             |          1.1 |            14 |          7 |         17 |                   13 |
| Charlotte         |          1   |            20 |         13 |         23 |                   22 |
| Washington DC     |          0   |            13 |          9 |         20 |                   11 |
| Orlando           |          0   |            16 |         10 |         20 |                   16 |
| Seattle           |          0   |            19 |         16 |         21 |                   20 |
| Minneapolis       |          0   |            20 |         13 |         23 |                   21 |
| Denver            |          0   |            15 |         13 |         16 |                   15 |
| Austin            |          0   |            24 |         20 |         25 |                   24 |
| Nashville         |          0   |            25 |         24 |         25 |                   25 |
| Pittsburgh        |          0   |            23 |         20 |         25 |                   23 |