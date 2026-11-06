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
| top_n_share | 0 | 0.0186 | 0.9666 |
| median_rank | 1 | 13 | 25 |
| p10_rank | 1 | 8 | 22 |
| p90_rank | 3 | 16 | 25 |

## Sample rows
| metro             |   top_n_share |   median_rank |   p10_rank |   p90_rank |
|:------------------|--------------:|--------------:|-----------:|-----------:|
| New York          |        0.5799 |             4 |          1 |         12 |
| Los Angeles       |        0.9117 |             2 |          1 |          5 |
| Chicago           |        0.3535 |             8 |          3 |         16 |
| Dallas-Fort Worth |        0.0026 |            17 |         10 |         22 |
| Houston           |        0.2727 |             7 |          4 |         13 |

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
| Miami             |         96.7 |             1 |          1 |          3 |                    1 |
| Los Angeles       |         91.2 |             2 |          1 |          5 |                    2 |
| Phoenix           |         64.6 |             4 |          2 |         10 |                    3 |
| New York          |         58   |             4 |          1 |         12 |                    4 |
| San Francisco     |         54.2 |             5 |          3 |         13 |                    5 |
| Chicago           |         35.4 |             8 |          3 |         16 |                    8 |
| Tampa             |         32.7 |             7 |          4 |         13 |                    7 |
| Houston           |         27.3 |             7 |          4 |         13 |                    6 |
| Orlando           |         12.2 |             9 |          5 |         14 |                    9 |
| Philadelphia      |         10.8 |            10 |          5 |         14 |                   11 |
| Atlanta           |          8.8 |             9 |          6 |         15 |                   10 |
| San Diego         |          3   |            15 |          8 |         19 |                   15 |
| Washington DC     |          1.9 |            13 |          7 |         18 |                   13 |
| Detroit           |          1.4 |            13 |          8 |         16 |                   12 |
| San Antonio       |          0.6 |            16 |          9 |         19 |                   16 |
| Sacramento        |          0.5 |            18 |         12 |         21 |                   19 |
| Boston            |          0.4 |            16 |          9 |         21 |                   17 |
| Dallas-Fort Worth |          0.3 |            17 |         10 |         22 |                   18 |
| Charlotte         |          0   |            22 |         19 |         23 |                   22 |
| Seattle           |          0   |            21 |         18 |         23 |                   21 |
| Minneapolis       |          0   |            19 |         16 |         22 |                   20 |
| Denver            |          0   |            15 |         12 |         16 |                   14 |
| Austin            |          0   |            23 |         18 |         25 |                   23 |
| Nashville         |          0   |            24 |         21 |         25 |                   24 |
| Pittsburgh        |          0   |            25 |         22 |         25 |                   25 |