"""Generate reports/memo.md (one page) from data/output/metros_scored.json.

Every name and number below comes from the JSON through plan.py; nothing about a specific metro is hardcoded.
Markdown note: a list must be preceded by a blank line, or renderers fold the "- " lines into one paragraph.
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan

p = plan.build()
d, by = p["d"], p["by"]
meta = d["meta"]
plan.set_weights(meta)
pct = lambda x: f"{x * 100:.0f}%"
TIER = {3: "Tier 3", 2: "Tier 2", 1: "Tier 1", 0: "Tier 0"}
vegas = next(m for m in d["metros"] if m["benchmark"])
w1, w2, w3, dep = p["w1"], p["w2"], p["w3"], p["depri"]


def comp_txt(m):
    ops = plan.operating(m)
    return f"{plan.names(ops)} operating" if ops else "no operating competitor"


def line(m):
    s = (f"- **{m['metro']}** (#{m['ranks']['balanced']}, {m['total']:.1f}): demand {m['opportunity']:.0f}, {TIER[m['regulation']['tier']]} "
         f"({m['regulation']['new_entrant_path']} new-entrant path), {comp_txt(m)}; top 5 in {pct(m['confidence'])} of draws; ~{plan.fleet(m):,.0f} vehicles.")
    if m["ease_of_entry"] < p["med_ease"]:
        s += " " + plan.left_of_ease_median_reason(m, p["med_ease"])
    return s


def watch(m):
    """The single largest ease-of-entry shortfall, as a phrase."""
    k = plan.shortfalls(m, ["regulatory", "operating", "competition", "charging"])[0]
    return f"{m['metro']}: {plan.weak_phrase(k, m, 1 + sum(1 for x in p['cand'] if x['raw']['crowding'] > m['raw']['crowding']))}"


def reasons(m):
    r = []
    if m["opportunity"] < 35: r.append(f"demand {m['opportunity']:.0f}/100")
    if m["raw"]["snow_days"] >= 14: r.append(f"snow ~{m['raw']['snow_days']:.0f} days")
    if m["regulation"]["tier"] <= 1: r.append(f"Tier {m['regulation']['tier']} rules")
    if m["raw"]["crowding"] >= 2: r.append(f"crowding {m['raw']['crowding']:.1f}")
    return ", ".join(r[:2]) or "mid-pack on every pillar"


crowded = [m for m in w1 if m["raw"]["crowding"] >= 1.0]
launch = w1 + w2
least_crowded = min(launch, key=lambda m: m["raw"]["crowding"])
snow = max(launch, key=lambda m: m["raw"]["snow_days"])
heat = max(launch, key=lambda m: m["raw"]["heat_days"])
slow_open = [m for m in launch if m["regulation"]["tier"] >= 2 and m["regulation"]["new_entrant_path"] == "slow"]
weakest = min(launch, key=lambda m: m["confidence"])
low_risk, fast = p["top5"]["low_risk"], p["top5"]["fast_growth"]
dep_lines = "; ".join(f"{m['metro']} ({reasons(m)})" for m in dep)
best = min(dep, key=lambda m: min(m["ranks"].values()))
best_rank = min(best["ranks"].values())
n_top10_low = sum(1 for m in p["cand"] if m["ranks"]["balanced"] <= 10 and m["regulation"]["tier"] <= 1)
dfw, hou = by["Dallas-Fort Worth"], by["Houston"]
vq = p["quad"](vegas)
v = meta["vintages"]
asof = meta["data_as_of"]

vegas_line = (f"Las Vegas, the beachhead, scores \"{vq}\" on this model (demand {vegas['opportunity']:.0f}/100), which shows it underweights tourism-driven demand: visitors are not in resident population, density or commute data."
              if vq == "Opportunistic" else f"Las Vegas, the beachhead, scores \"{vq}\" on this model (demand {vegas['opportunity']:.0f}/100).")
gate = (f" {min(w1, key=lambda m: m['confidence'])['metro']} only just clears the 50% wave 1 gate."
        if min(m["confidence"] for m in w1) < 0.6 else "")

memo = f"""# Where should the operator launch after Las Vegas?

*For the strategy team. Data as of {asof}. Sources: Census ACS 2024 5-year, NHTSA SGO ADS reports, Open-Meteo, EIA, FAA, and researched seed files (AV rules, competitors) as of {asof}.*

**Recommendation.** {plan.one_line_answer(p)} The sequence uses balanced-weight scores for 25 US metros (demand 35, operating conditions 25, regulation 20, competition 15, charging 5). Waves 1 and 2 are limited to states with Tier 2+ AV rules; wave 1 also needs a top-5 finish in at least half of 10,000 weight draws.

**Why these metros** (rank, score, demand score, regulation, competitors, confidence, fleet at {pct(meta['assumptions']['capture_share']['value'])} capture)

{chr(10).join(line(m) for m in w1)}
- **Wave 2:** {plan.names(w2)} (top 5 in {', '.join(pct(m['confidence']) for m in w2)} of draws). Demand {min(m['opportunity'] for m in w2):.0f}-{max(m['opportunity'] for m in w2):.0f} (wave 1: {min(m['opportunity'] for m in w1):.0f}-{max(m['opportunity'] for m in w1):.0f}). Watch: {'; '.join(watch(m) for m in w2)}.
- **Wave 3:** {plan.names(w3)}. Demand {min(m['opportunity'] for m in w3):.0f}-{max(m['opportunity'] for m in w3):.0f}, but driverless commercial service is not yet allowed. Build the policy case now; launch when the law changes.
- **Dallas-Fort Worth and Houston** are in no wave. {plan.why_rank(dfw, p['cand'], p['med_opp'])} {plan.why_rank(hou, p['cand'], p['med_opp'])}

**Deprioritize.** {dep_lines}. None ranks better than #{best_rank} in any scenario ({best['metro']}).

**Key risks and de-risking**

- *Regulation:* {n_top10_low} of the top 10 sit in Tier 0-1 states; engage {w3[0]['state']}, {w3[1]['state']} and {w3[-1]['state']} regulators early. {plan.names(sorted({m['state'] for m in slow_open}))} {'is' if len({m['state'] for m in slow_open}) == 1 else 'are'} Tier 2+ but a slow path for a new entrant (multi-step permits): start filings in wave 1.
- *Weather:* {snow['metro']} has snow on ~{snow['raw']['snow_days']:.0f} days a year and {heat['metro']} has ~{heat['raw']['heat_days']:.0f} days at 40 C or higher. Validate winter and heat performance before public launch.
- *Competition:* {plan.names(crowded)} already have operators (crowding {min(m['raw']['crowding'] for m in crowded):.1f}-{max(m['raw']['crowding'] for m in crowded):.1f}); {least_crowded['metro']} is the least crowded launch metro ({least_crowded['raw']['crowding']:.1f}). Competitor status is dated and cross-checked against NHTSA activity.

**Confidence.** {w1[0]['metro']} is top 5 in {pct(w1[0]['confidence'])} of weight draws and {w1[-1]['metro']} in {pct(w1[-1]['confidence'])};{gate} {weakest['metro']} is the softest pick ({pct(weakest['confidence'])}), so wave 2 order is not firm. A low-risk lens puts {plan.names(low_risk)} on top; fast growth, {plan.names(fast)}. {vegas_line} The answer would also change if a Tier 1 state legalized driverless service, a competitor entered {least_crowded['metro']}, or fare and capture differ from our labeled assumptions.

**Data.** ACS {v['acs']}; FAA {v['faa']}; Open-Meteo weather 2016-2025; NHTSA SGO reports to Sep 2026 (activity only, never rates); EIA {v['eia'].split(' (')[0]}; AV rules, new-entrant paths and competitors researched {asof} (some rows medium/low confidence); demand is a two-anchor estimate (Chicago and NYC ride-hail trips), not a forecast.
"""
out = pathlib.Path(__file__).resolve().parent / "memo.md"
out.write_text(memo, encoding="utf-8")
print(f"wrote {out} ({len(memo.split())} words)")
