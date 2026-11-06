# Profile: 08_features
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| state | str | 0 |
| principal_city | str | 0 |
| benchmark | bool | 0 |
| metro_pop | float64 | 0 |
| city_pop | float64 | 0 |
| city_households | float64 | 0 |
| city_hh_no_vehicle | float64 | 0 |
| city_workers | float64 | 0 |
| city_taxi_ridehail | float64 | 0 |
| city_median_hh_income | float64 | 0 |
| no_vehicle_share | float64 | 0 |
| taxi_ridehail_share | float64 | 0 |
| land_sqmi | float64 | 0 |
| city_density | float64 | 0 |
| enplanements | float64 | 0 |
| enplanements_per_resident | float64 | 0 |
| rain_days | float64 | 0 |
| snow_days | float64 | 0 |
| heat_days | float64 | 0 |
| elec_cents_kwh | float64 | 0 |
| reg_tier | int64 | 0 |
| crowding | float64 | 0 |
| n_competitors | int64 | 0 |
| log_metro_pop | float64 | 0 |

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
| land_sqmi | 36 | 140.3 | 640.8 |
| city_density | 1,451 | 4,676 | 2.823e+04 |
| enplanements | 4.792e+06 | 2.564e+07 | 7.054e+07 |
| enplanements_per_resident | 1.964 | 4.549 | 13.31 |
| rain_days | 12.9 | 93.9 | 131.9 |
| snow_days | 0 | 0.75 | 24.6 |
| heat_days | 0 | 0 | 69.6 |
| elec_cents_kwh | 8.6 | 13.04 | 26.96 |
| reg_tier | 1 | 3 | 3 |
| crowding | 0.3 | 0.7 | 2.4 |
| n_competitors | 1 | 1 | 4 |
| log_metro_pop | 14.55 | 15.25 | 16.8 |

## Sample rows
| metro             | state   | principal_city   | benchmark   |   metro_pop |    city_pop |   city_households |   city_hh_no_vehicle |     city_workers |   city_taxi_ridehail |   city_median_hh_income |   no_vehicle_share |   taxi_ridehail_share |   land_sqmi |   city_density |   enplanements |   enplanements_per_resident |   rain_days |   snow_days |   heat_days |   elec_cents_kwh |   reg_tier |   crowding |   n_competitors |   log_metro_pop |
|:------------------|:--------|:-----------------|:------------|------------:|------------:|------------------:|---------------------:|-----------------:|---------------------:|------------------------:|-------------------:|----------------------:|------------:|---------------:|---------------:|----------------------------:|------------:|------------:|------------:|-----------------:|-----------:|-----------:|----------------:|----------------:|
| New York          | NY      | New York         | False       | 1.97985e+07 | 8.48384e+06 |       3.33409e+06 |          1.84471e+06 |      3.9268e+06  |                43641 |                   80483 |          0.553287  |            0.0111136  |     300.483 |       28234    |    7.05358e+07 |                     3.56268 |        99.8 |        10.1 |         0.2 |            22.93 |          1 |        0.4 |               1 |         16.8011 |
| Los Angeles       | CA      | Los Angeles      | False       | 1.29745e+07 | 3.85726e+06 |       1.4391e+06  |     171011           |      1.89678e+06 |                 7771 |                   81939 |          0.118832  |            0.00409694 |     470.518 |        8197.91 |    4.71048e+07 |                     3.63057 |        26.8 |         0   |         2   |            26.96 |          3 |        1.4 |               2 |         16.3785 |
| Chicago           | IL      | Chicago          | False       | 9.3716e+06  | 2.71123e+06 |       1.1602e+06  |     308497           |      1.36437e+06 |                10620 |                   77902 |          0.265899  |            0.00778384 |     227.748 |       11904.5  |    5.00484e+07 |                     5.34044 |        97.9 |        18.2 |         0   |            14.05 |          1 |        0.3 |               1 |         16.0532 |
| Dallas-Fort Worth | TX      | Dallas           | False       | 7.98559e+06 | 1.30793e+06 |  533915           |      47064           | 662654           |                 1385 |                   70518 |          0.0881489 |            0.00209008 |     339.685 |        3850.42 |    4.94484e+07 |                     6.1922  |        86.4 |         0.8 |         3.9 |             8.6  |          3 |        2.4 |               4 |         15.8931 |
| Houston           | TX      | Houston          | False       | 7.44279e+06 | 2.32825e+06 |  930404           |      93572           |      1.12467e+06 |                 4914 |                   64813 |          0.100571  |            0.00436929 |     640.819 |        3633.25 |    3.00553e+07 |                     4.03818 |       119.1 |         0.4 |         0.2 |             8.6  |          3 |        1.4 |               2 |         15.8228 |

## Sanity checks
- [PASS] 26 rows, no nulls
- [PASS] exactly one benchmark (Las Vegas)
- [PASS] crowding >= 0