"""Validate the two seed CSVs, land them as parquet, and cross-check competitor_presence against NHTSA activity."""
import pandas as pd
from common import *

SEED = ROOT / "data/seed"
reg = pd.read_csv(SEED / "state_av_regulation.csv", dtype=str, keep_default_na=False)
comp = pd.read_csv(SEED / "competitor_presence.csv", dtype=str, keep_default_na=False)
m = load_metros()

# ---- validation
req_src = ["source_url", "source_title", "as_of_date", "confidence"]
reg["tier"] = reg.tier.astype(int)
checks = [
    ("regulation covers every state of the 26 metros", set(m.state) <= set(reg.state)),
    ("regulation: one row per state", reg.state.is_unique),
    ("regulation: tier in 0-3", reg.tier.between(0, 3).all()),
    ("regulation: source fields filled", bool((reg[req_src] != "").all().all())),
    ("regulation: confidence values valid", reg.confidence.isin(["high", "medium", "low"]).all()),
    ("regulation: new_entrant_path is fast | moderate | slow", reg.new_entrant_path.isin(["fast", "moderate", "slow"]).all()),
    ("regulation: new-entrant source fields filled", bool((reg[["new_entrant_rationale", "new_entrant_source_url", "new_entrant_source_title", "new_entrant_as_of_date", "new_entrant_confidence"]] != "").all().all())),
    ("regulation: new-entrant confidence values valid", reg.new_entrant_confidence.isin(["high", "medium", "low"]).all()),
    ("competitors: metro names all in metros.yaml", set(comp.metro) <= set(m["name"])),
    ("competitors: status values valid", comp.status.isin(["operating_public", "operating_limited", "testing", "announced"]).all()),
    ("competitors: source fields filled", bool((comp[req_src] != "").all().all())),
    ("competitors: is_operator is true or false", comp.is_operator.isin(["true", "false"]).all()),
    ("competitors: no duplicate (metro, competitor)", not comp.duplicated(["metro", "competitor"]).any()),
]
reg.to_parquet(INTERIM / "regulation.parquet", index=False)
comp.to_parquet(INTERIM / "competitors.parquet", index=False)

# ---- cross-check vs NHTSA
nh = pd.read_parquet(INTERIM / "nhtsa.parquet")
CANON = {"Waymo": "Waymo", "Zoox": "Zoox", "Tesla": "Tesla", "Avride": "Avride", "May Mobility": "May Mobility",
         "Nuro": "Nuro", "Motional": "Motional", "Beep": "Beep", "MOIA America": "MOIA"}
nh["competitor"] = nh.operating_entity.map(lambda s: next((v for k, v in CANON.items() if s.startswith(k)), s))
nh_agg = nh.groupby(["metro", "competitor"], as_index=False).ads_incidents.sum()
MIN = 5  # ignore tiny counts as noise
SEED_KEY = {"Nuro/Lucid": "Nuro"}   # seed names a partnership, NHTSA names the operator
rows = []
for metro in sorted(set(m["name"])):
    seed_c = comp[comp.metro == metro].assign(competitor=lambda d: d.competitor.replace(SEED_KEY))
    seed_active = set(seed_c[seed_c.status.isin(["operating_public", "operating_limited", "testing"])].competitor)
    seed_ann = set(seed_c[seed_c.status == "announced"].competitor)
    nh_c = nh_agg[(nh_agg.metro == metro) & (nh_agg.ads_incidents >= MIN)]
    nh_set = set(nh_c.competitor)
    miss_seed = sorted(nh_set - seed_active - seed_ann)
    ann_no_nh = sorted(seed_ann - set(nh_agg[nh_agg.metro == metro].competitor))
    rows.append(dict(metro=metro, seed_active=", ".join(sorted(seed_active)) or "-", seed_announced=", ".join(sorted(seed_ann)) or "-",
                     nhtsa_active=", ".join(f"{r.competitor} ({r.ads_incidents})" for r in nh_c.itertuples()) or "-",
                     nhtsa_not_in_seed=", ".join(miss_seed) or "-", announced_without_nhtsa=", ".join(ann_no_nh) or "-"))
xc = pd.DataFrame(rows)
flag_a = xc[xc.nhtsa_not_in_seed != "-"]
flag_b = xc[xc.announced_without_nhtsa != "-"]
review = pd.concat([reg[reg.confidence == "low"].assign(file="regulation", item=lambda d: d.state),
                    reg[reg.new_entrant_confidence == "low"].assign(file="regulation (new-entrant path)", item=lambda d: d.state),
                    comp[comp.confidence == "low"].assign(file="competitors", item=lambda d: d.metro + " / " + d.competitor)])
extra = "\n".join([
    f"## Cross-check: seed competitor_presence vs NHTSA ADS incidents (24 months, operators with >= {MIN} incidents in the metro)",
    xc.to_markdown(index=False), "",
    "### Flag A: NHTSA shows activity the seed file lacks", flag_a[["metro", "nhtsa_not_in_seed", "nhtsa_active"]].to_markdown(index=False) if len(flag_a) else "none", "",
    "### Flag B: announced in seed but no NHTSA activity (expected for cities not yet launched)", flag_b[["metro", "announced_without_nhtsa"]].to_markdown(index=False) if len(flag_b) else "none", "",
    "## Needs human review (low-confidence rows; sources not opened or status not stated)",
    review[["file", "item", "confidence", "source_title"]].to_markdown(index=False), "",
    "### Rows researched on 2026-11-06 and notes",
    "- All 26 metros have at least one sourced row. Every status comes from a page opened during the research (company pages, TechCrunch, Electrek, Insurance Journal, PhillyVoice, an SEC investor deck).",
    "- Waymo access tiers: operating_public = waymo.com/whereyoucango says anyone can ride, or press reports of the waitlist ending; Denver and Las Vegas are 'gradually adding riders' = operating_limited. The waymo.com page is undated and lags press reports for Houston and San Antonio, so those two cite the press report and are medium confidence.",
    "- Tesla rows rest partly on a fan site (Miami launch, upcoming-city list); Austin, Dallas, Houston and the Bay Area rest on Electrek. Tesla Orlando and Tampa: one search result claimed unsupervised rides began there but no opened source confirms it, so they stay 'announced'.",
    "- Zoox: Atlanta and Los Angeles are 'testing' (mapping/testing, no public rides) per Electrek 2026-03-24. Washington DC is low confidence: the source (2025-09-30) describes mapping with safety drivers and planned autonomous testing; no newer source found.",
    "- Avride Austin rests on a Wikipedia page (secondary source), medium confidence; it is consistent with NHTSA showing 29 Avride incidents in Austin.",
    "- Not included (could not verify from an opened source as current): May Mobility Detroit (a 2024 pilot for select residents, run through 2026), Motional Pittsburgh, Tesla Orlando/Tampa as operating.",
    "- Platform partners were recorded only where an opened page stated them.",
    "- Waymo Washington DC stays 'announced' (waymo.com Up Next) although NHTSA shows 6 Waymo incidents there, so some testing is likely. Not changed because no opened source states it.",
])
ok = write_profile("07_seed_and_crosscheck", comp, checks, extra=extra)
xc.to_csv(INTERIM / "crosscheck.csv", index=False)
raise SystemExit(0 if ok else 1)
