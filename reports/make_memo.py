"""Generate reports/memo.md (one page) from data/output/metros_scored.json."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan

p = plan.build()
d, by = p["d"], p["by"]
meta = d["meta"]
pct = lambda x: f"{x * 100:.0f}%"
TIER = {3: "Tier 3", 2: "Tier 2", 1: "Tier 1", 0: "Tier 0"}


def comp_txt(m):
    c = [x["competitor"] for x in m["competitors"] if x["status"] in ("operating_public", "operating_limited")]
    return f"{', '.join(c)} operating" if c else "no operating competitor"


def line(m):
    return (f"- **{m['metro']}** (#{m['ranks']['balanced']}, {m['total']:.1f}): demand {m['opportunity']:.0f}, {TIER[m['regulation']['tier']]}, "
            f"{comp_txt(m)}; top 5 in {pct(m['confidence'])} of draws; ~{plan.fleet(m):,.0f} vehicles.")


def reasons(m):
    r = []
    if m["opportunity"] < 35: r.append(f"demand {m['opportunity']:.0f}/100")
    if m["raw"]["snow_days"] >= 14: r.append(f"snow ~{m['raw']['snow_days']:.0f} days")
    if m["regulation"]["tier"] <= 1: r.append(f"Tier {m['regulation']['tier']} rules")
    if m["raw"]["crowding"] >= 2: r.append(f"crowding {m['raw']['crowding']:.1f}")
    return ", ".join(r[:2]) or "mid-pack on every pillar"

w1, w2, w3, dep = p["w1"], p["w2"], p["w3"], p["depri"]
crowded = [m for m in w1 if m["raw"]["crowding"] >= 1.0]
open_field = [m for m in w1 if m["raw"]["crowding"] < 1.0]
snow = max(w1 + w2, key=lambda m: m["raw"]["snow_days"])
heat = max(w1 + w2, key=lambda m: m["raw"]["heat_days"])
t1 = ", ".join(f"{m['metro']} ({m['state']})" for m in w3)
w2txt = f"{plan.names(w2)} (top 5 in {', '.join(pct(m['confidence']) for m in w2)} of draws)"
weakest = sorted([m for m in w1 + w2], key=lambda m: m["confidence"])[0]
low_risk, fast = p["top5"]["low_risk"], p["top5"]["fast_growth"]
ph = by["Phoenix"] if "Phoenix" in by else None
xc_flags = "Atlanta, Austin, Dallas-Fort Worth and Houston"
dep_lines = "; ".join(f"{m['metro']} ({reasons(m)})" for m in dep)
best = min(dep, key=lambda m: min(m["ranks"].values()))
best_rank = min(best["ranks"].values())

memo = f"""# Where should the operator launch after Las Vegas?

*For the strategy team. Data as of {meta['data_as_of']}; every number is generated from `data/output/metros_scored.json`.*

**Recommendation.** {plan.one_line_answer(p)} The sequence uses balanced-weight scores for 25 US metros (demand 35, operating conditions 25, regulation 20, competition 15, charging 5). Waves 1 and 2 are limited to states with Tier 2+ AV rules; wave 1 also needs a top-5 finish in at least half of 10,000 weight draws.

**Why these metros** (rank, score, demand score, regulation tier, competitors, confidence, fleet at {pct(meta['assumptions']['capture_share']['value'])} capture)
{chr(10).join(line(m) for m in w1)}
- **Wave 2:** {w2txt}. Demand scores of {min(m['opportunity'] for m in w2):.0f}-{max(m['opportunity'] for m in w2):.0f} (wave 1: {min(m['opportunity'] for m in w1):.0f}-{max(m['opportunity'] for m in w1):.0f}) and weather to validate (Atlanta rain ~{by['Atlanta']['raw']['rain_days']:.0f} days, Phoenix heat ~{by['Phoenix']['raw']['heat_days']:.0f} days), so they follow once wave 1 proves the playbook.
- **Wave 3:** {t1}. Demand scores of {min(m['opportunity'] for m in w3):.0f}-{max(m['opportunity'] for m in w3):.0f}, but driverless commercial service is not yet allowed. Build the policy case now; launch when the law changes.

**Deprioritize.** {dep_lines}. None ranks better than #{best_rank} in any scenario ({best['metro']}).

**Key risks and de-risking**
- *Regulation:* {len(w3)} of the top 10 sit in Tier 0-1 states. Engage {w3[0]['state']}, {w3[1]['state']} and {w3[-1]['state']} regulators early; track permit steps in Tier 2 states such as {by['Philadelphia']['state']}.
- *Weather:* {snow['metro']} has snow on ~{snow['raw']['snow_days']:.0f} days a year and {heat['metro']} has ~{heat['raw']['heat_days']:.0f} days at 40 C or higher. Validate winter and heat performance before public launch.
- *Competition:* {plan.names(crowded)} already have operators (crowding {min(m['raw']['crowding'] for m in crowded):.1f}-{max(m['raw']['crowding'] for m in crowded):.1f}); {plan.names(open_field)} is the open field ({open_field[0]['raw']['crowding']:.1f}). NHTSA reports show operators the seed file lacks in {xc_flags}, so crowding there is likely understated.

**Confidence.** {w1[0]['metro']} is top 5 in {pct(w1[0]['confidence'])} of weight draws and {w1[-1]['metro']} in {pct(w1[-1]['confidence'])}; {weakest['metro']} is the softest pick ({pct(weakest['confidence'])}), so wave 2 order is not firm. A low-risk lens puts {plan.names(low_risk)} on top; fast growth, {plan.names(fast)}. The answer would also change if a Tier 1 state legalized driverless service, a competitor entered {open_field[0]['metro']}, or fare and capture differ from our labeled assumptions.

**Data.** ACS {meta['vintages']['acs']}; FAA {meta['vintages']['faa']}; weather 2016-2025; NHTSA reports to Sep 2026 (activity only, never rates); EIA {meta['vintages']['eia'].split(' (')[0]}; regulation and competitors researched {meta['data_as_of']} (some rows medium/low confidence); demand is a two-anchor estimate, not a forecast. Method: `docs/methodology.md`.
"""
out = pathlib.Path(__file__).resolve().parent / "memo.md"
out.write_text(memo, encoding="utf-8")
print(f"wrote {out} ({len(memo.split())} words)")
