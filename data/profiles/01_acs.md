# Profile: 01_acs
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| cbsa | str | 0 |
| place_geoid | str | 0 |
| metro_pop | float64 | 0 |
| city_pop | float64 | 0 |
| city_households | float64 | 0 |
| city_hh_no_vehicle | float64 | 0 |
| city_workers | float64 | 0 |
| city_taxi_ridehail | float64 | 0 |
| city_median_hh_income | float64 | 0 |
| no_vehicle_share | float64 | 0 |
| taxi_ridehail_share | float64 | 0 |
| acs_vintage | str | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| metro_pop | 2.08e+06 | 4.219e+06 | 1.98e+07 |
| city_pop | 3.048e+05 | 7.365e+05 | 8.484e+06 |
| city_households | 1.312e+05 | 3.494e+05 | 3.334e+06 |
| city_hh_no_vehicle | 9,709 | 3.766e+04 | 1.845e+06 |
| city_workers | 1.562e+05 | 4.389e+05 | 3.927e+06 |
| city_taxi_ridehail | 471 | 1,584 | 4.364e+04 |
| city_median_hh_income | 3.994e+04 | 8.066e+04 | 1.41e+05 |
| no_vehicle_share | 0.06414 | 0.111 | 0.5533 |
| taxi_ridehail_share | 0.001867 | 0.004244 | 0.01111 |

## Sample rows
| metro             |   cbsa |   place_geoid |   metro_pop |    city_pop |   city_households |   city_hh_no_vehicle |     city_workers |   city_taxi_ridehail |   city_median_hh_income |   no_vehicle_share |   taxi_ridehail_share | acs_vintage             |
|:------------------|-------:|--------------:|------------:|------------:|------------------:|---------------------:|-----------------:|---------------------:|------------------------:|-------------------:|----------------------:|:------------------------|
| New York          |  35620 |       3651000 | 1.97985e+07 | 8.48384e+06 |       3.33409e+06 |          1.84471e+06 |      3.9268e+06  |                43641 |                   80483 |          0.553287  |            0.0111136  | 2024 5-year (2020-2024) |
| Los Angeles       |  31080 |       0644000 | 1.29745e+07 | 3.85726e+06 |       1.4391e+06  |     171011           |      1.89678e+06 |                 7771 |                   81939 |          0.118832  |            0.00409694 | 2024 5-year (2020-2024) |
| Chicago           |  16980 |       1714000 | 9.3716e+06  | 2.71123e+06 |       1.1602e+06  |     308497           |      1.36437e+06 |                10620 |                   77902 |          0.265899  |            0.00778384 | 2024 5-year (2020-2024) |
| Dallas-Fort Worth |  19100 |       4819000 | 7.98559e+06 | 1.30793e+06 |  533915           |      47064           | 662654           |                 1385 |                   70518 |          0.0881489 |            0.00209008 | 2024 5-year (2020-2024) |
| Houston           |  26420 |       4835000 | 7.44279e+06 | 2.32825e+06 |  930404           |      93572           |      1.12467e+06 |                 4914 |                   64813 |          0.100571  |            0.00436929 | 2024 5-year (2020-2024) |

## Sanity checks
- [PASS] all 26 metros present
- [PASS] NYC metro pop roughly 19-20M
- [PASS] shares between 0 and 1
- [PASS] no nulls in numeric fields
- [PASS] NYC no-vehicle share > 0.4

Source: ACS 5-year 2024 API. Variables: {"B01003_001E": "pop", "B08201_001E": "households", "B08201_002E": "hh_no_vehicle", "B08301_001E": "workers_16plus", "B08301_016E": "taxi_ridehail_commuters", "B19013_001E": "median_hh_income"}