# Profile: 05_weather
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| days | int64 | 0 |
| missing_values | int64 | 0 |
| rain_days | float64 | 0 |
| snow_days | float64 | 0 |
| heat_days | float64 | 0 |
| weather_vintage | str | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| days | 3,653 | 3,653 | 3,653 |
| missing_values | 0 | 0 | 0 |
| rain_days | 12.9 | 93.9 | 131.9 |
| snow_days | 0 | 0.75 | 24.6 |
| heat_days | 0 | 0 | 69.6 |

## Sample rows
| metro             |   days |   missing_values |   rain_days |   snow_days |   heat_days | weather_vintage                     |
|:------------------|-------:|-----------------:|------------:|------------:|------------:|:------------------------------------|
| New York          |   3653 |                0 |        99.8 |        10.1 |         0.2 | 2016-2025 daily, Open-Meteo archive |
| Los Angeles       |   3653 |                0 |        26.8 |         0   |         2   | 2016-2025 daily, Open-Meteo archive |
| Chicago           |   3653 |                0 |        97.9 |        18.2 |         0   | 2016-2025 daily, Open-Meteo archive |
| Dallas-Fort Worth |   3653 |                0 |        86.4 |         0.8 |         3.9 | 2016-2025 daily, Open-Meteo archive |
| Houston           |   3653 |                0 |       119.1 |         0.4 |         0.2 | 2016-2025 daily, Open-Meteo archive |

## Sanity checks
- [PASS] all 26 present with 3,653 days and no missing values
- [PASS] Phoenix and Las Vegas are top-2 heat days
- [PASS] Phoenix/Vegas rain days below median
- [PASS] Minneapolis, Boston, Detroit in top 7 snow days (Denver and Chicago also high)
- [PASS] Miami and Florida metros have zero snow days