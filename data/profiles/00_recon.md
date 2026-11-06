# Phase 0 recon profile
metros.yaml: 26 rows (25 candidates + Las Vegas benchmark), 26 unique CBSA codes, 26 unique place GEOIDs. CBSA codes and place FIPS are from Census delineation and Gazetteer files, none typed from memory.
Every CBSA and place code resolves in the Census API: the Phase 1 ACS ingest (with the API key) returned data for all 26 metros and principal cities (see 01_acs.md). At Phase 0 this was blocked by the missing key.
Airports: all codes found in the FAA CY2025 file after mapping Miami PBI -> DJT.
Sanity: ATL is #2 by metro enplanements (NYC metro #1 with JFK/LGA/EWR); LAS 26.5M, high for its size.
Needs human review: nothing from Phase 0 itself. Seed-CSV review items are tracked in 07_seed_and_crosscheck.md.
