# Profile: 06_eia
rows: 51

## Columns
| column | dtype | nulls |
|---|---|---|
| state_name | str | 0 |
| commercial_cents_kwh | float64 | 0 |
| state | str | 0 |
| eia_period | str | 0 |

## Numeric summary
| column | min | median | max |
|---|---|---|---|
| commercial_cents_kwh | 7.72 | 12.7 | 42.43 |

## Sample rows
| state_name    |   commercial_cents_kwh | state   | eia_period      |
|:--------------|-----------------------:|:--------|:----------------|
| Connecticut   |                  21.75 | CT      | August 2026 YTD |
| Maine         |                  22.83 | ME      | August 2026 YTD |
| Massachusetts |                  24.66 | MA      | August 2026 YTD |
| New Hampshire |                  21.4  | NH      | August 2026 YTD |
| Rhode Island  |                  23.68 | RI      | August 2026 YTD |

## Sanity checks
- [PASS] all states of the 26 metros present
- [PASS] values for the study states in 8-30 c/kWh

Outside 8-30 nationally (not used by any metro): ND 7.72, HI 42.43. Table 5.6.B, commercial sector, August 2026 YTD: a year-to-date average, not a 12-month average (chosen by user). by State, Year-to-Date through August 2026 and 2025 (Cents per Kilowatthour)