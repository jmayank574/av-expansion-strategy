# Profile: 10_demand
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| city_pop | float64 | 0 |
| taxi_ridehail_share | float64 | 0 |
| no_vehicle_share | float64 | 0 |
| density_per_sqmi | float64 | 0 |
| enplanements_per_resident | float64 | 0 |
| demand_index | float64 | 0 |
| tpr_low | float64 | 0 |
| tpr_base | float64 | 0 |
| tpr_high | float64 | 0 |
| trips_low | float64 | 0 |
| trips_base | float64 | 0 |
| trips_high | float64 | 0 |
| est_from_chicago | float64 | 0 |
| est_from_nyc | float64 | 0 |
| anchor_year | int64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| city_pop | 3.048e+05 | 7.365e+05 | 8.484e+06 |
| taxi_ridehail_share | 0.001867 | 0.004244 | 0.01111 |
| no_vehicle_share | 0.06414 | 0.111 | 0.5533 |
| density_per_sqmi | 1,451 | 4,676 | 2.823e+04 |
| enplanements_per_resident | 1.964 | 4.549 | 13.31 |
| demand_index | 1.093 | 1.986 | 4.987 |
| tpr_low | 6.295 | 11.43 | 34.49 |
| tpr_base | 8.373 | 15.2 | 34.49 |
| tpr_high | 11.14 | 20.22 | 40.44 |
| trips_low | 3.095e+06 | 9.235e+06 | 2.436e+08 |
| trips_base | 4.116e+06 | 1.228e+07 | 2.436e+08 |
| trips_high | 5.474e+06 | 1.634e+07 | 2.436e+08 |
| est_from_chicago | 11.14 | 20.22 | 50.79 |
| est_from_nyc | 6.295 | 11.43 | 28.71 |
| anchor_year | 2,025 | 2,025 | 2,025 |

## Sample rows
| metro             |    city_pop |   taxi_ridehail_share |   no_vehicle_share |   density_per_sqmi |   enplanements_per_resident |   demand_index |   tpr_low |   tpr_base |   tpr_high |   trips_low |   trips_base |   trips_high |   est_from_chicago |   est_from_nyc |   anchor_year |
|:------------------|------------:|----------------------:|-------------------:|-------------------:|----------------------------:|---------------:|----------:|-----------:|-----------:|------------:|-------------:|-------------:|-------------------:|---------------:|--------------:|
| New York          | 8.48384e+06 |            0.0111136  |          0.553287  |           28234    |                     3.56268 |        4.987   |  28.7122  |    28.7122 |    28.7122 | 2.4359e+08  |  2.4359e+08  |  2.4359e+08  |            50.787  |       28.7122  |          2025 |
| Los Angeles       | 3.85726e+06 |            0.00409694 |          0.118832  |            8197.91 |                     3.63057 |        1.95105 |  11.233   |    14.9396 |    19.8692 | 4.33286e+07 |  5.76259e+07 |  7.66409e+07 |            19.8692 |       11.233   |          2025 |
| Chicago           | 2.71123e+06 |            0.00778384 |          0.265899  |           11904.5  |                     5.34044 |        3.38688 |  34.4916  |    34.4916 |    34.4916 | 9.35144e+07 |  9.35144e+07 |  9.35144e+07 |            34.4916 |       19.4996  |          2025 |
| Dallas-Fort Worth | 1.30793e+06 |            0.00209008 |          0.0881489 |            3850.42 |                     6.1922  |        1.44772 |   8.33509 |    11.0855 |    14.7434 | 1.09017e+07 |  1.4499e+07  |  1.92833e+07 |            14.7434 |        8.33509 |          2025 |
| Houston           | 2.32825e+06 |            0.00436929 |          0.100571  |            3633.25 |                     4.03818 |        1.59346 |   9.17421 |    12.2015 |    16.2276 | 2.13599e+07 |  2.84081e+07 |  3.7782e+07  |            16.2276 |        9.17421 |          2025 |

## Sanity checks
- [PASS] NYC estimate reproduces observed trips per resident
- [PASS] Chicago estimate reproduces observed trips per resident
- [PASS] low <= base <= high for every metro
- [PASS] Las Vegas trips per resident are in the top half of the 26 metros (high relative to its size)
- [PASS] all estimates positive and finite

Anchors (calendar 2025): Chicago TNP trips 93,514,416 / 2,711,226 residents = 34.5 per resident; NYC HVFHV trips 243,589,684 / 8,483,844 = 28.7 per resident.
Observed anchor ratio (NYC/Chicago trips per resident): 0.83; demand-index ratio: 1.47.
The anchors do not rank the way the index does (Chicago has more trips per resident than NYC despite a lower index), which is why the spread between the two anchor-based estimates is wide.
Las Vegas base trips per resident 15.5 (rank 13 of 26 including NYC and Chicago); city population rank 18 of 26.

## Estimates (annual ride-hail trips per principal-city resident and total trips, millions)
| metro             |         city_pop |   demand_index |   tpr_low |   tpr_base |   tpr_high |   trips_low |   trips_base |   trips_high |
|:------------------|-----------------:|---------------:|----------:|-----------:|-----------:|------------:|-------------:|-------------:|
| New York          |      8.48384e+06 |          4.987 |      28.7 |       28.7 |       28.7 |       243.6 |        243.6 |        243.6 |
| Los Angeles       |      3.85726e+06 |          1.951 |      11.2 |       14.9 |       19.9 |        43.3 |         57.6 |         76.6 |
| Chicago           |      2.71123e+06 |          3.387 |      34.5 |       34.5 |       34.5 |        93.5 |         93.5 |         93.5 |
| Dallas-Fort Worth |      1.30793e+06 |          1.448 |       8.3 |       11.1 |       14.7 |        10.9 |         14.5 |         19.3 |
| Houston           |      2.32825e+06 |          1.593 |       9.2 |       12.2 |       16.2 |        21.4 |         28.4 |         37.8 |
| Washington DC     | 681294           |          3.37  |      19.4 |       25.8 |       34.3 |        13.2 |         17.6 |         23.4 |
| Philadelphia      |      1.57971e+06 |          2.604 |      15   |       19.9 |       26.5 |        23.7 |         31.5 |         41.9 |
| Miami             | 459745           |          3.471 |      20   |       26.6 |       35.3 |         9.2 |         12.2 |         16.2 |
| Atlanta           | 505268           |          2.282 |      13.1 |       17.5 |       23.2 |         6.6 |          8.8 |         11.7 |
| Boston            | 666442           |          3.546 |      20.4 |       27.2 |       36.1 |        13.6 |         18.1 |         24.1 |
| Phoenix           |      1.64232e+06 |          1.375 |       7.9 |       10.5 |       14   |        13   |         17.3 |         23   |
| San Francisco     | 830235           |          3.971 |      22.9 |       30.4 |       40.4 |        19   |         25.2 |         33.6 |
| Detroit           | 638530           |          2.371 |      13.7 |       18.2 |       24.1 |         8.7 |         11.6 |         15.4 |
| Seattle           | 754195           |          2.138 |      12.3 |       16.4 |       21.8 |         9.3 |         12.3 |         16.4 |
| Minneapolis       | 427246           |          2.267 |      13.1 |       17.4 |       23.1 |         5.6 |          7.4 |          9.9 |
| San Diego         |      1.38953e+06 |          1.216 |       7   |        9.3 |       12.4 |         9.7 |         12.9 |         17.2 |
| Tampa             | 401618           |          1.46  |       8.4 |       11.2 |       14.9 |         3.4 |          4.5 |          6   |
| Denver            | 718877           |          2.091 |      12   |       16   |       21.3 |         8.7 |         11.5 |         15.3 |
| Orlando           | 319758           |          1.78  |      10.2 |       13.6 |       18.1 |         3.3 |          4.4 |          5.8 |
| Charlotte         | 903844           |          1.449 |       8.3 |       11.1 |       14.8 |         7.5 |         10   |         13.3 |
| San Antonio       |      1.47984e+06 |          1.123 |       6.5 |        8.6 |       11.4 |         9.6 |         12.7 |         16.9 |
| Austin            | 979539           |          1.236 |       7.1 |        9.5 |       12.6 |         7   |          9.3 |         12.3 |
| Nashville         | 690130           |          1.093 |       6.3 |        8.4 |       11.1 |         4.3 |          5.8 |          7.7 |
| Pittsburgh        | 304759           |          1.764 |      10.2 |       13.5 |       18   |         3.1 |          4.1 |          5.5 |
| Sacramento        | 528706           |          1.24  |       7.1 |        9.5 |       12.6 |         3.8 |          5   |          6.7 |
| Las Vegas         | 660400           |          2.02  |      11.6 |       15.5 |       20.6 |         7.7 |         10.2 |         13.6 |