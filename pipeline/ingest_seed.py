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
    ("competitors: metro names all in metros.yaml", set(comp.metro) <= set(m["name"])),
    ("competitors: status values valid", comp.status.isin(["operating_public", "operating_limited", "testing", "announced"]).all()),
    ("competitors: source fields filled", bool((comp[req_src] != "").all().all())),
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
rows = []
for metro in sorted(set(m["name"])):
    seed_c = comp[comp.metro == metro]
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
                    comp[comp.confidence == "low"].assign(file="competitors", item=lambda d: d.metro + " / " + d.competitor)])
extra = "\n".join([
    f"## Cross-check: seed competitor_presence vs NHTSA ADS incidents (24 months, operators with >= {MIN} incidents in the metro)",
    xc.to_markdown(index=False), "",
    "### Flag A: NHTSA shows activity the seed file lacks", flag_a[["metro", "nhtsa_not_in_seed", "nhtsa_active"]].to_markdown(index=False) if len(flag_a) else "none", "",
    "### Flag B: announced in seed but no NHTSA activity (expected for cities not yet launched)", flag_b[["metro", "announced_without_nhtsa"]].to_markdown(index=False) if len(flag_b) else "none", "",
    "## Needs human review (low-confidence rows; sources not opened or status not stated)",
    review[["file", "item", "confidence", "source_title"]].to_markdown(index=False), "",
    "### Dropped rows (could not verify from an opened source)",
    "- competitor_presence: Nuro/Lucid (San Francisco, announced) and May Mobility/Lyft (Atlanta, announced). The only pages found were search results that I did not open.",
    "- Waymo city-level 'operating_limited' vs 'operating_public' for Dallas, Houston, Miami, Nashville, Orlando, San Antonio is my judgment from search extracts: waymo.com does not state access tiers.",
    "- Platform partners were recorded only where an opened page stated them (Waymo on Uber in Atlanta and Austin).",
    "- Tesla rows rest on a fan/news site rather than Tesla filings.",
])
ok = write_profile("07_seed_and_crosscheck", comp, checks, extra=extra)
xc.to_csv(INTERIM / "crosscheck.csv", index=False)
raise SystemExit(0 if ok else 1)
