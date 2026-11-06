"""Add demand estimates, unit economics and Monte Carlo confidence to data/output/metros_scored.json (idempotent)."""
import sys, json, pathlib, yaml, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))
from common import *

OUT = ROOT / "data/output/metros_scored.json"
d = json.load(open(OUT))
A = yaml.safe_load(open(ROOT / "config/assumptions.yaml"))
dem = pd.read_parquet(INTERIM / "demand.parquet").set_index("metro")
ue = pd.read_parquet(INTERIM / "unit_economics.parquet")
mc = pd.read_parquet(INTERIM / "monte_carlo.parquet").set_index("metro")


def clean(x):
    return None if x is None or (isinstance(x, float) and x != x) else (float(x) if isinstance(x, (int, float)) or hasattr(x, "item") else x)


for m in d["metros"]:
    n = m["metro"]
    r = dem.loc[n]
    m["demand_estimate"] = {k: float(r[k]) for k in ["tpr_low", "tpr_base", "tpr_high", "trips_low", "trips_base", "trips_high", "city_pop"]}
    m["unit_economics"] = {c: {k: clean(v) for k, v in ue[(ue.metro == n) & (ue.case == c)].iloc[0].drop(["metro", "case"]).items()} for c in ["low", "base", "high"]}
    if n in mc.index:
        m["confidence"] = float(mc.loc[n, "top_n_share"])
        m["median_rank"] = float(mc.loc[n, "median_rank"])
        m["rank_p10"], m["rank_p90"] = float(mc.loc[n, "p10_rank"]), float(mc.loc[n, "p90_rank"])
    else:
        m["confidence"] = m["median_rank"] = m["rank_p10"] = m["rank_p90"] = None
d["meta"]["assumptions"] = A["assumptions"]
d["meta"]["monte_carlo"] = A["monte_carlo"]
d["meta"]["demand_method"] = dict(
    anchor_year=int(dem.anchor_year.iloc[0]),
    anchors={"Chicago": dict(source="Chicago Transportation Network Providers trips (data.cityofchicago.org, dataset 6dvr-xwnh), SoQL count", tpr=float(dem.loc["Chicago", "tpr_base"])),
             "New York": dict(source="NYC TLC High Volume FHV trip records, monthly row counts from parquet footers", tpr=float(dem.loc["New York", "tpr_base"]))},
    note="Estimate from two anchors scaled by a demand index; not a forecast.")
d["meta"]["vintages"]["demand"] = f"Chicago TNP and NYC HVFHV calendar {int(dem.anchor_year.iloc[0])}"
# wave membership of the balanced plan, from the same rules the memo and deck use (reports/plan.py), so the app can label them
sys.path.insert(0, str(ROOT / "reports"))
import plan
pl = plan.build(d)
wave = {m["metro"]: w for w, ms in ((1, pl["w1"]), (2, pl["w2"]), (3, pl["w3"])) for m in ms}
for m in d["metros"]:
    m["wave"] = wave.get(m["metro"])
json.dump(d, open(OUT, "w"), indent=1)
print("enriched", len(d["metros"]), "metros")
