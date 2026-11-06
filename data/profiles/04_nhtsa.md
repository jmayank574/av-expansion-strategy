# Profile: 04_nhtsa
rows: 49

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| operating_entity | str | 0 |
| ads_incidents | int64 | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| ads_incidents | 1 | 5 | 691 |

## Sample rows
| metro   | operating_entity     |   ads_incidents |
|:--------|:---------------------|----------------:|
| Atlanta | May Mobility         |              13 |
| Atlanta | Waymo                |              77 |
| Austin  | Avride               |              29 |
| Austin  | International Motors |               1 |
| Austin  | MOIA America         |               1 |

## Sanity checks
- [PASS] no duplicate Same Incident ID
- [PASS] no duplicate Report ID
- [PASS] window is 24 months
- [PASS] Waymo is the top operating entity
- [PASS] majority of incidents mapped to a metro

Raw rows 3890 (current + archive) -> latest version per Report ID 3449 -> window 2024-10..2026-09 -> one per Same Incident ID 2219.
Mapped by city/state: 1824; mapped by Gazetteer city point (<=40 km of downtown): 320; unmapped: 75.

## Top operating entities
| operating_entity   |   count |
|:-------------------|--------:|
| Waymo              |    1887 |
| Zoox               |     110 |
| Avride             |      83 |
| Tesla              |      36 |
| May Mobility       |      27 |
| Motional           |      21 |
| Aurora Operations  |      11 |
| Nuro               |       8 |
| Beep               |       5 |
| MOIA America       |       5 |

## Top cities
|                         |   n |
|:------------------------|----:|
| ('San Francisco', 'CA') | 697 |
| ('Los Angeles', 'CA')   | 359 |
| ('Austin', 'TX')        | 242 |
| ('Phoenix', 'AZ')       | 188 |
| ('Atlanta', 'GA')       |  87 |
| ('Dallas', 'TX')        |  75 |
| ('Tempe', 'AZ')         |  74 |
| ('Las Vegas', 'NV')     |  59 |
| ('Scottsdale', 'AZ')    |  48 |
| ('Houston', 'TX')       |  28 |
| ('Miami', 'FL')         |  28 |
| ('Santa Monica', 'CA')  |  25 |

## Incidents by metro (candidates + benchmark)
| metro             |   n |
|:------------------|----:|
| San Francisco     | 741 |
| Los Angeles       | 467 |
| Phoenix           | 339 |
| Austin            | 243 |
| Atlanta           |  90 |
| Dallas-Fort Worth |  85 |
| Las Vegas         |  69 |
| Miami             |  31 |
| Houston           |  30 |
| Orlando           |  11 |
| Nashville         |  10 |
| Washington DC     |   7 |
| Philadelphia      |   5 |
| San Antonio       |   5 |
| Denver            |   4 |
| San Diego         |   2 |
| Detroit           |   2 |
| Minneapolis       |   1 |
| Pittsburgh        |   1 |
| Tampa             |   1 |

## Unmapped cities (top 25)
|                           |   n |
|:--------------------------|----:|
| ('Mountain View', 'CA')   |  15 |
| ('Palo Alto', 'CA')       |   9 |
| ('Santa Clara', 'CA')     |   7 |
| ('San Jose', 'CA')        |   5 |
| ('Sunnyvale', 'CA')       |   5 |
| ('Jacksonville', 'FL')    |   4 |
| ('Ann Arbor', 'MI')       |   2 |
| ('Aledo', 'TX')           |   2 |
| ('', 'TX')                |   1 |
| ('', '')                  |   1 |
| ('Fairfield', 'TX')       |   1 |
| ('Gainesville', 'TX')     |   1 |
| ('Grand Rapids', 'MN')    |   1 |
| ('Centerville', 'TX')     |   1 |
| ('Deming', 'NM')          |   1 |
| ('Edgewood', 'NM')        |   1 |
| ('El Paso', 'TX')         |   1 |
| ('Del Valle', 'TX')       |   1 |
| ('Mount Pleasant', 'PA')  |   1 |
| ('Menlo Park', 'CA')      |   1 |
| ('Lowell', 'AR')          |   1 |
| ('Las Cruces', 'NM')      |   1 |
| ('Harbor City', 'CA')     |   1 |
| ('Peoria', 'AZ')          |   1 |
| ('Oak Ridge North', 'TX') |   1 |

NHTSA SGO reports carry no mileage: counts show where operators are active, not safety rates.