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
| top_n_share | 0 | 0.0239 | 0.9809 |
| median_rank | 1 | 13 | 25 |
| p10_rank | 1 | 8 | 23 |
| p90_rank | 2 | 18 | 25 |

## Sample rows
| metro             |   top_n_share |   median_rank |   p10_rank |   p90_rank |
|:------------------|--------------:|--------------:|-----------:|-----------:|
| New York          |        0.1353 |            10 |          5 |         18 |
| Los Angeles       |        0.8643 |             3 |          2 |          7 |
| Chicago           |        0.4088 |             7 |          3 |         15 |
| Dallas-Fort Worth |        0.0071 |            15 |          8 |         21 |
| Houston           |        0.0239 |            13 |          8 |         18 |

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
| San Francisco     |         98.1 |             1 |          1 |          2 |                    1 |
| Los Angeles       |         86.4 |             3 |          2 |          7 |                    2 |
| Miami             |         81.2 |             3 |          2 |          7 |                    3 |
| Philadelphia      |         57.3 |             5 |          2 |          9 |                    4 |
| Chicago           |         40.9 |             7 |          3 |         15 |                    7 |
| Phoenix           |         37.3 |             7 |          4 |         12 |                    5 |
| Atlanta           |         27.1 |             8 |          4 |         12 |                    5 |
| San Diego         |         24.8 |             9 |          4 |         16 |                    9 |
| Washington DC     |         18.3 |             8 |          4 |         16 |                    8 |
| New York          |         13.5 |            10 |          5 |         18 |                   10 |
| Sacramento        |          7.5 |            13 |          6 |         19 |                   12 |
| Detroit           |          2.8 |            11 |          8 |         16 |                   11 |
| Houston           |          2.4 |            13 |          8 |         18 |                   13 |
| Seattle           |          0.8 |            14 |         10 |         18 |                   15 |
| Dallas-Fort Worth |          0.7 |            15 |          8 |         21 |                   17 |
| San Antonio       |          0.6 |            17 |         10 |         21 |                   19 |
| Tampa             |          0   |            14 |          9 |         17 |                   14 |
| Charlotte         |          0   |            22 |         17 |         23 |                   22 |
| Boston            |          0   |            15 |          9 |         20 |                   16 |
| Minneapolis       |          0   |            21 |         16 |         24 |                   20 |
| Orlando           |          0   |            17 |         11 |         19 |                   18 |
| Denver            |          0   |            21 |         20 |         23 |                   21 |
| Austin            |          0   |            24 |         19 |         25 |                   24 |
| Nashville         |          0   |            25 |         23 |         25 |                   25 |
| Pittsburgh        |          0   |            23 |         19 |         24 |                   23 |