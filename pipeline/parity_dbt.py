"""Parity check: dbt mart_metro_scores must equal the Python scores (metros_scored.json) to 2 decimals. Fails loudly."""
import json, sys, duckdb
from common import *

d = json.load(open(ROOT / "data/output/metros_scored.json"))
con = duckdb.connect(str(ROOT / "data/av_expansion.duckdb"), read_only=True)
mart = {r[0]: r for r in con.execute("select * from mart_metro_scores").fetchall()}
cols = [c[0] for c in con.description]
bad, worst, n = [], 0.0, 0
for m in d["metros"]:
    row = dict(zip(cols, mart[m["metro"]]))
    pairs = [(f"total_{k}", row[f"total_{k}"], m["totals"][k]) for k in m["totals"]]
    pairs += [(f"pillar_{p}", row[p], v) for p, v in m["pillar_scores"].items()]
    pairs += [("ease_of_entry", row["ease_of_entry"], m["ease_of_entry"])]
    for name, a, b in pairs:
        n += 1
        diff = abs(a - b); worst = max(worst, diff)
        if round(a, 2) != round(b, 2) and diff >= 0.005:
            bad.append((m["metro"], name, a, b))
    for k, r in m["ranks"].items():
        if row[f"rank_{k}"] != r:
            bad.append((m["metro"], f"rank_{k}", row[f"rank_{k}"], r))
print(f"parity: compared {n} values for {len(d['metros'])} metros; max abs diff {worst:.2e}")
if bad:
    print("PARITY FAILED:")
    for b in bad[:30]: print("  ", b)
    sys.exit(1)
print("PARITY OK: dbt mart equals Python scores to 2 decimals (and ranks identical)")
