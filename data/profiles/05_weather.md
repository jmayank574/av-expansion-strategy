# Profile: 05_weather
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| days | int64 | 0 |
| missing_values | int64 | 0 |
| missing_pct | float64 | 0 |
| rain_days | float64 | 0 |
| snow_days | float64 | 0 |
| heat_days | float64 | 0 |
| weather_source | str | 0 |
| weather_station | str | 0 |
| station_name | str | 0 |
| station_km_from_city | float64 | 0 |
| snow_days_reported | int64 | 0 |
| om_rain_days | float64 | 0 |
| om_snow_days | float64 | 0 |
| om_heat_days | float64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| days | 3,653 | 3,653 | 3,653 |
| missing_values | 0 | 0 | 20 |
| missing_pct | 0 | 0 | 0.55 |
| rain_days | 10.4 | 73.15 | 93.8 |
| snow_days | 0 | 0.65 | 23.8 |
| heat_days | 0 | 0 | 89.3 |
| station_km_from_city | 2.6 | 13.8 | 30.5 |
| snow_days_reported | 0 | 3,653 | 3,653 |
| om_rain_days | 12.9 | 93.9 | 131.9 |
| om_snow_days | 0 | 0.75 | 24.6 |
| om_heat_days | 0 | 0 | 69.6 |

## Sample rows
| metro             |   days |   missing_values |   missing_pct |   rain_days |   snow_days |   heat_days | weather_source   | weather_station   | station_name                |   station_km_from_city |   snow_days_reported |   om_rain_days |   om_snow_days |   om_heat_days |
|:------------------|-------:|-----------------:|--------------:|------------:|------------:|------------:|:-----------------|:------------------|:----------------------------|-----------------------:|---------------------:|---------------:|---------------:|---------------:|
| New York          |   3653 |                0 |          0    |        76.6 |         6.8 |         0   | NOAA GHCN-Daily  | USW00094789       | JFK INTL AP                 |                   22.1 |                 3653 |           99.8 |           10.1 |            0.2 |
| Los Angeles       |   3653 |                0 |          0    |        19.5 |         0   |         0.1 | NOAA GHCN-Daily  | USW00023174       | LOS ANGELES INTL AP         |                   18.3 |                   30 |           26.8 |            0   |            2   |
| Chicago           |   3653 |                0 |          0    |        74.7 |        17.4 |         0   | NOAA GHCN-Daily  | USW00094846       | CHICAGO OHARE INTL AP       |                   26.3 |                 3653 |           97.9 |           18.2 |            0   |
| Dallas-Fort Worth |   3653 |                2 |          0.05 |        53   |         0.8 |         5.9 | NOAA GHCN-Daily  | USW00003927       | DAL-FTW WSCMO AP            |                   23.8 |                 3653 |           86.4 |            0.8 |            3.9 |
| Houston           |   3653 |                0 |          0    |        64.4 |         0.3 |         1   | NOAA GHCN-Daily  | USW00012960       | HOUSTON INTERCONTINENTAL AP |                   24.6 |                 3653 |          119.1 |            0.4 |            0.2 |

## Sanity checks
- [PASS] all 26 present, 3,653 days each
- [PASS] every station is missing no more than 5% of days (else Open-Meteo fallback is used)
- [PASS] Phoenix and Las Vegas are top-2 heat days
- [PASS] Phoenix/Vegas rain days below median
- [PASS] Minneapolis, Boston, Detroit in top 7 snow days (Denver and Chicago also high)
- [PASS] Miami and Florida metros have zero snow days
- [PASS] no metro shows zero snow days at a station while Open-Meteo shows 3+ (would mean the station does not report snowfall)

Metros using the Open-Meteo fallback: 0

## NOAA station vs Open-Meteo archive (days per year; om_* is Open-Meteo)
| metro             | weather_station   | station_name                   |   missing_pct |   rain_days |   om_rain_days |   snow_days |   om_snow_days |   heat_days |   om_heat_days |
|:------------------|:------------------|:-------------------------------|--------------:|------------:|---------------:|------------:|---------------:|------------:|---------------:|
| New York          | USW00094789       | JFK INTL AP                    |           0   |        76.6 |           99.8 |         6.8 |           10.1 |         0   |            0.2 |
| Los Angeles       | USW00023174       | LOS ANGELES INTL AP            |           0   |        19.5 |           26.8 |         0   |            0   |         0.1 |            2   |
| Chicago           | USW00094846       | CHICAGO OHARE INTL AP          |           0   |        74.7 |           97.9 |        17.4 |           18.2 |         0   |            0   |
| Dallas-Fort Worth | USW00003927       | DAL-FTW WSCMO AP               |           0   |        53   |           86.4 |         0.8 |            0.8 |         5.9 |            3.9 |
| Houston           | USW00012960       | HOUSTON INTERCONTINENTAL AP    |           0   |        64.4 |          119.1 |         0.3 |            0.4 |         1   |            0.2 |
| Washington DC     | USW00013743       | WASHINGTON REAGAN NATL AP      |           0   |        73.2 |          103.4 |         3.7 |            6.5 |         0.1 |            0   |
| Philadelphia      | USW00013739       | PHILA INTL AP                  |           0   |        76.2 |           98.8 |         6.2 |            7.7 |         0   |            0   |
| Miami             | USW00012839       | MIAMI INTL AP                  |           0   |        92   |          131.9 |         0   |            0   |         0   |            0   |
| Atlanta           | USW00013874       | ATLANTA HARTSFIELD-JACKSON INT |           0   |        77   |          108.5 |         0.5 |            0.7 |         0   |            0   |
| Boston            | USW00014739       | BOSTON                         |           0   |        78.8 |           94.8 |        11.2 |           14.3 |         0   |            0   |
| Phoenix           | USW00023183       | PHOENIX AP                     |           0   |        16.5 |           24.6 |         0   |            0   |        89.3 |           69.6 |
| San Francisco     | USW00023234       | SAN FRANCISCO INTL AP          |           0.6 |        38.1 |           47   |         0   |            0   |         0.2 |            0   |
| Detroit           | USW00094847       | DETROIT METRO AP               |           0   |        73.1 |           93   |        22.1 |           17.2 |         0   |            0   |
| Seattle           | USW00024233       | SEATTLE TACOMA AP              |           0.2 |        93.8 |          114.5 |         3.4 |            6.8 |         0.2 |            0   |
| Minneapolis       | USW00014922       | MINNEAPOLIS-ST PAUL INTL AP    |           0   |        63.6 |           79.5 |        23.8 |           22.3 |         0   |            0   |
| San Diego         | USW00023188       | SAN DIEGO INTL AP              |           0   |        20.5 |           27.8 |         0   |            0   |         0   |            0   |
| Tampa             | USW00012842       | TAMPA INTL AP                  |           0   |        73.6 |          117   |         0   |            0   |         0   |            0   |
| Denver            | USW00003017       | DENVER INTL AP                 |           0   |        34.3 |           46.7 |        20.9 |           24.6 |         0.1 |            0   |
| Orlando           | USW00012815       | ORLANDO INTL AP                |           0   |        75.3 |          128.8 |         0   |            0   |         0   |            0   |
| Charlotte         | USW00013881       | CHARLOTTE DOUGLAS AP           |           0   |        76.6 |           89.5 |         0.8 |            2.5 |         0   |            0.1 |
| San Antonio       | USW00012921       | SAN ANTONIO INTL AP            |           0   |        41.9 |           76.6 |         0.4 |            0.6 |         5.2 |            3   |
| Austin            | USW00013904       | AUSTIN BERGSTROM INTL AP       |           0   |        46.4 |           84.5 |         0.3 |            0.6 |         5.2 |            2.8 |
| Nashville         | USW00013897       | NASHVILLE INTL AP              |           0   |        86   |          118.5 |         2.7 |            3.5 |         0   |            0   |
| Pittsburgh        | USW00094823       | PITTSBURGH ASOS                |           0   |        91.2 |          115.3 |        21.9 |           16   |         0   |            0   |
| Sacramento        | USW00093225       | SACRAMENTO METRO AP            |           0.5 |        35.8 |           47.9 |         0   |            0.2 |         8   |           14.3 |
| Las Vegas         | USW00023169       | MCCARRAN INTL AP               |           0   |        10.4 |           12.9 |         0.1 |            0.2 |        60.8 |           55   |