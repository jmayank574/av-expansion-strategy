# Profile: 03_faa
rows: 26

## Columns
| column | dtype | nulls |
|---|---|---|
| metro | str | 0 |
| airports | str | 0 |
| enplanements | float64 | 0 |
| metro_pop | float64 | 0 |
| enplanements_per_resident | float64 | 0 |
| faa_vintage | str | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| enplanements | 4.792e+06 | 2.564e+07 | 7.054e+07 |
| metro_pop | 2.08e+06 | 4.219e+06 | 1.98e+07 |
| enplanements_per_resident | 1.964 | 4.549 | 13.31 |

## Sample rows
| metro             | airports        |   enplanements |   metro_pop |   enplanements_per_resident | faa_vintage   |
|:------------------|:----------------|---------------:|------------:|----------------------------:|:--------------|
| New York          | JFK,LGA,EWR     |    7.05358e+07 | 1.97985e+07 |                     3.56268 | CY2025        |
| Los Angeles       | LAX,BUR,LGB,SNA |    4.71048e+07 | 1.29745e+07 |                     3.63057 | CY2025        |
| Chicago           | ORD,MDW         |    5.00484e+07 | 9.3716e+06  |                     5.34044 | CY2025        |
| Dallas-Fort Worth | DFW,DAL         |    4.94484e+07 | 7.98559e+06 |                     6.1922  | CY2025        |
| Houston           | IAH,HOU         |    3.00553e+07 | 7.44279e+06 |                     4.03818 | CY2025        |

## Sanity checks
- [PASS] all 26 present
- [PASS] Atlanta among top 3 by enplanements
- [PASS] Vegas per-resident rank is 1 or 2 of 26

Miami uses DJT (FAA Locid for West Palm Beach, IATA PBI).