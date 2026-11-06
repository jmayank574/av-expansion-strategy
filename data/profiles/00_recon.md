# Phase 0 recon profile
metros.yaml: 26 rows (25 candidates + Las Vegas benchmark), 26 unique CBSA codes, 26 unique place GEOIDs. CBSA codes and place FIPS are from Census delineation and Gazetteer files, none typed from memory.
Not done: "every code resolves in the Census API". Blocked by the missing API key.
Airports: all codes found in the FAA CY2025 file after mapping Miami PBI -> DJT.
Sanity: ATL is #2 by metro enplanements (NYC metro #1 with JFK/LGA/EWR); LAS 26.5M, high for its size.
Needs human review: none yet (seed CSVs not started).
