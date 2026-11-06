# Profile: 11_unit_economics
rows: 78

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| case | str | 0 |
| city_ride_hail_trips_year | float64 | 0 |
| addressable_trips_per_day | float64 | 0 |
| fleet_vehicles | float64 | 0 |
| revenue_per_vehicle | float64 | 0 |
| miles_per_vehicle | float64 | 0 |
| charging_cost_per_vehicle | float64 | 0 |
| opex_per_vehicle | float64 | 0 |
| contribution_per_vehicle | float64 | 0 |
| payback_years | float64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| city_ride_hail_trips_year | 3.095e+06 | 1.254e+07 | 2.436e+08 |
| addressable_trips_per_day | 84.79 | 1,125 | 5.339e+04 |
| fleet_vehicles | 7.066 | 56.09 | 2,136 |
| revenue_per_vehicle | 6.57e+04 | 1.314e+05 | 2.281e+05 |
| miles_per_vehicle | 3.942e+04 | 6.022e+04 | 9.125e+04 |
| charging_cost_per_vehicle | 1,865 | 3,651 | 8,610 |
| opex_per_vehicle | 6.099e+04 | 6.978e+04 | 8.161e+04 |
| contribution_per_vehicle | 724.8 | 6.162e+04 | 1.524e+05 |
| payback_years | 0.6563 | 2.272 | 275.9 |

## Sample rows
| metro       | case   |   city_ride_hail_trips_year |   addressable_trips_per_day |   fleet_vehicles |   revenue_per_vehicle |   miles_per_vehicle |   charging_cost_per_vehicle |   opex_per_vehicle |   contribution_per_vehicle |   payback_years |
|:------------|:-------|----------------------------:|----------------------------:|-----------------:|----------------------:|--------------------:|----------------------------:|-------------------:|---------------------------:|----------------:|
| New York    | low    |                 2.4359e+08  |                     6673.69 |         556.141  |                 65700 |               39420 |                     4971.45 |            64101.5 |                   1598.55  |      125.114    |
| New York    | base   |                 2.4359e+08  |                    20021.1  |        1112.28   |                131400 |               60225 |                     6214.32 |            72461.8 |                  58938.2   |        2.37537  |
| New York    | high   |                 2.4359e+08  |                    53389.5  |        2135.58   |                228125 |               91250 |                     7323.27 |            80323.3 |                 147802     |        0.676582 |
| Los Angeles | low    |                 4.33286e+07 |                     1187.08 |          98.9237 |                 65700 |               39420 |                     5845.2  |            64975.2 |                    724.802 |      275.937    |
| Los Angeles | base   |                 5.76259e+07 |                     4736.37 |         263.132  |                131400 |               60225 |                     7306.5  |            73554   |                  57846     |        2.42022  |

## Sanity checks
- [PASS] every assumption has value, low, high, source_url and rationale
- [PASS] every assumption is sourced or labeled
- [PASS] base case matches a hand calculation (Phoenix)
- [PASS] low <= base <= high contribution per vehicle for every metro
- [PASS] base payback between 0.5 and 10 years
- [PASS] no negative fleets

Cases: low = pessimistic end of every input and the low demand estimate; base = central values; high = optimistic end and the high demand estimate.
Revenue, cost and payback per vehicle do not depend on demand; demand only sets the fleet size.

## Base case, all candidates
| metro             |   addressable_trips_per_day |   fleet_vehicles |   revenue_per_vehicle |   opex_per_vehicle |   contribution_per_vehicle |   payback_years |
|:------------------|----------------------------:|-----------------:|----------------------:|-------------------:|---------------------------:|----------------:|
| New York          |                     20021.1 |           1112.3 |                131400 |            72461.8 |                    58938.2 |             2.4 |
| Los Angeles       |                      4736.4 |            263.1 |                131400 |            73554   |                    57846   |             2.4 |
| Chicago           |                      7686.1 |            427   |                131400 |            70055.2 |                    61344.8 |             2.3 |
| Dallas-Fort Worth |                      1191.7 |             66.2 |                131400 |            68578.2 |                    62821.8 |             2.2 |
| Houston           |                      2334.9 |            129.7 |                131400 |            68578.2 |                    62821.8 |             2.2 |
| Washington DC     |                      1444.9 |             80.3 |                131400 |            72670.5 |                    58729.5 |             2.4 |
| Philadelphia      |                      2588.7 |            143.8 |                131400 |            70014.6 |                    61385.4 |             2.3 |
| Miami             |                      1004.2 |             55.8 |                131400 |            69440   |                    61960   |             2.3 |
| Atlanta           |                       725.8 |             40.3 |                131400 |            69502.4 |                    61897.6 |             2.3 |
| Boston            |                      1487.4 |             82.6 |                131400 |            72930.7 |                    58469.3 |             2.4 |
| Phoenix           |                      1421.6 |             79   |                131400 |            69575.5 |                    61824.5 |             2.3 |
| San Francisco     |                      2074.9 |            115.3 |                131400 |            73554   |                    57846   |             2.4 |
| Detroit           |                       952.8 |             52.9 |                131400 |            70529.5 |                    60870.5 |             2.3 |
| Seattle           |                      1014.9 |             56.4 |                131400 |            69461.7 |                    61938.3 |             2.3 |
| Minneapolis       |                       609.7 |             33.9 |                131400 |            69689.4 |                    61710.6 |             2.3 |
| San Diego         |                      1063.2 |             59.1 |                131400 |            73554   |                    57846   |             2.4 |
| Tampa             |                       368.9 |             20.5 |                131400 |            69440   |                    61960   |             2.3 |
| Denver            |                       946   |             52.6 |                131400 |            69870.9 |                    61529.1 |             2.3 |
| Orlando           |                       358.2 |             19.9 |                131400 |            69440   |                    61960   |             2.3 |
| Charlotte         |                       824.4 |             45.8 |                131400 |            69122.9 |                    62277.1 |             2.2 |
| San Antonio       |                      1046.2 |             58.1 |                131400 |            68578.2 |                    62821.8 |             2.2 |
| Austin            |                       761.8 |             42.3 |                131400 |            68578.2 |                    62821.8 |             2.2 |
| Nashville         |                       474.9 |             26.4 |                131400 |            69925.1 |                    61474.9 |             2.3 |
| Pittsburgh        |                       338.3 |             18.8 |                131400 |            70014.6 |                    61385.4 |             2.3 |
| Sacramento        |                       412.5 |             22.9 |                131400 |            73554   |                    57846   |             2.4 |
| Las Vegas         |                       839.6 |             46.6 |                131400 |            68784.2 |                    62615.8 |             2.2 |

## Assumptions
|                           |     value |       low |      high | source_url                                                                                                                                                                                                                                                                                                                                   |
|:--------------------------|----------:|----------:|----------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| capture_share             |      0.03 |      0.01 |      0.08 | analyst assumption                                                                                                                                                                                                                                                                                                                           |
| avg_fare_usd              |     20    |     15    |     25    | https://techcrunch.com/2026/01/27/the-price-gap-between-waymo-and-uber-is-narrowing                                                                                                                                                                                                                                                          |
| trips_per_vehicle_per_day |     18    |     12    |     25    | analyst assumption                                                                                                                                                                                                                                                                                                                           |
| avg_trip_miles            |      5.5  |      4.5  |      7    | analyst assumption                                                                                                                                                                                                                                                                                                                           |
| deadhead_share            |      0.4  |      0.5  |      0.3  | analyst assumption                                                                                                                                                                                                                                                                                                                           |
| cost_per_mile_usd         |      1.1  |      1.5  |      0.8  | https://www.softwareseni.com/the-hidden-human-economy-inside-robotaxi-per-mile-costs (Sacra estimate: Waymo about $1.40 per mile all-in, Tesla about $0.81); https://newsroom.aaa.com/wp-content/uploads/2025/09/AAA-Brochure-Your-Driving-Cost-9.2025.pdf (AAA 2025: private-car maintenance 11.04 cents per mile, insurance $1,694 a year) |
| kwh_per_mile              |      0.45 |      0.55 |      0.35 | analyst assumption                                                                                                                                                                                                                                                                                                                           |
| vehicle_cost_usd          | 140000    | 200000    | 100000    | https://thenextweb.com/news/waymo-ojai-robotaxi-geely-sixth-generation-fleet-cost                                                                                                                                                                                                                                                            |