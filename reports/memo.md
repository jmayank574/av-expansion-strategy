# Where should the operator launch after Las Vegas?

*For the strategy team. Data as of 2026-11-05; every number is generated from `data/output/metros_scored.json`.*

**Recommendation.** Enter San Francisco, Los Angeles, Miami and Philadelphia first, then Atlanta, Phoenix and San Diego; hold Chicago, Washington DC and New York until the rules change. The sequence uses balanced-weight scores for 25 US metros (demand 35, operating conditions 25, regulation 20, competition 15, charging 5). Waves 1 and 2 are limited to states with Tier 2+ AV rules; wave 1 also needs a top-5 finish in at least half of 10,000 weight draws.

**Why these metros** (rank, score, demand score, regulation tier, competitors, confidence, fleet at 3% capture)
- **San Francisco** (#1, 64.0): demand 76, Tier 3, Zoox, Waymo operating; top 5 in 98% of draws; ~115 vehicles.
- **Los Angeles** (#2, 59.6): demand 63, Tier 3, Waymo operating; top 5 in 86% of draws; ~263 vehicles.
- **Miami** (#3, 59.0): demand 78, Tier 3, Waymo, Tesla operating; top 5 in 81% of draws; ~56 vehicles.
- **Philadelphia** (#4, 55.7): demand 69, Tier 2, no operating competitor; top 5 in 57% of draws; ~144 vehicles.
- **Wave 2:** Atlanta, Phoenix and San Diego (top 5 in 27%, 37%, 25% of draws). Demand scores of 26-61 (wave 1: 63-78) and weather to validate (Atlanta rain ~108 days, Phoenix heat ~70 days), so they follow once wave 1 proves the playbook.
- **Wave 3:** Chicago (IL), Washington DC (DC), New York (NY). Demand scores of 78-92, but driverless commercial service is not yet allowed. Build the policy case now; launch when the law changes.

**Deprioritize.** Orlando (demand 34/100); San Antonio (demand 20/100); Minneapolis (snow ~22 days, Tier 1 rules); Denver (snow ~25 days); Charlotte (demand 22/100); Pittsburgh (snow ~16 days); Austin (demand 18/100, crowding 2.1); Nashville (demand 12/100). None ranks better than #6 in any scenario (San Antonio).

**Key risks and de-risking**
- *Regulation:* 3 of the top 10 sit in Tier 0-1 states. Engage IL, DC and NY regulators early; track permit steps in Tier 2 states such as PA.
- *Weather:* Philadelphia has snow on ~8 days a year and Phoenix has ~70 days at 40 C or higher. Validate winter and heat performance before public launch.
- *Competition:* San Francisco, Los Angeles and Miami already have operators (crowding 1.4-1.8); Philadelphia is the open field (0.3). NHTSA reports show operators the seed file lacks in Atlanta, Austin, Dallas-Fort Worth and Houston, so crowding there is likely understated.

**Confidence.** San Francisco is top 5 in 98% of weight draws and Philadelphia in 57%; San Diego is the softest pick (25%), so wave 2 order is not firm. A low-risk lens puts San Francisco, Los Angeles, San Diego, Phoenix and Miami on top; fast growth, San Francisco, Miami, New York, Los Angeles and Chicago. The answer would also change if a Tier 1 state legalized driverless service, a competitor entered Philadelphia, or fare and capture differ from our labeled assumptions.

**Data.** ACS 2024 5-year (2020-2024); FAA CY2025 enplanements; weather 2016-2025; NHTSA reports to Sep 2026 (activity only, never rates); EIA August 2026 YTD; regulation and competitors researched 2026-11-05 (some rows medium/low confidence); demand is a two-anchor estimate, not a forecast. Method: `docs/methodology.md`.
