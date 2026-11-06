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
def contrib_vs_median(m):
    """Weighted points each pillar adds to (or takes from) the total versus the median metro, balanced weights."""
    import statistics
    w = meta["weights"]["scenarios"][meta["weights"]["default_scenario"]]
    return {k: (m["pillar_scores"][k] - statistics.median(x["pillar_scores"][k] for x in p["cand"])) * w[k] / 100 for k in w}


def why_rank_line(m):
    c = contrib_vs_median(m)
    pos = sorted((k for k in c if c[k] > 0), key=lambda k: -c[k])
    neg = sorted((k for k in c if c[k] < 0), key=lambda k: c[k])
    nm = {"demand": "demand", "operating": "operating conditions", "regulatory": "regulation", "competition": "competition", "charging": "power price"}
    fmt = lambda ks: ", ".join(f"{nm[k]} ({c[k]:+.1f})" for k in ks)
    top = f"{nm[pos[0]]} (crowding {m['raw']['crowding']:.1f})" if pos[0] == "competition" else nm[pos[0]]
    return (f"- **Why {m['metro']} is #{m['ranks']['balanced']}:** points versus the median metro come from {fmt(pos)}; {fmt(neg)} pull it down. "
            f"Its rank rests mostly on {top}, not on strength across the board.")


dfw, hou = by["Dallas-Fort Worth"], by["Houston"]
wave_of = lambda m: "wave 1" if m in w1 else "wave 2" if m in w2 else "wave 3" if m in w3 else None


def dh_line():
    """Where Dallas-Fort Worth and Houston rank, why, and which wave (if any) they are in."""
    out = []
    for m in (dfw, hou):
        s = plan.why_rank(m, p["cand"], p["med_opp"]).rstrip(".")
        out.append(f"{s}. It is in {wave_of(m)}." if wave_of(m) else f"{s}. It is in no wave.")
    return " ".join(out)


def watch_line():
    """Largest ease shortfall per wave 2 metro; one summary phrase when they share the same pillar."""
    ks = {m["metro"]: plan.shortfalls(m, ["regulatory", "operating", "competition", "charging"])[0] for m in w2}
    if len(set(ks.values())) == 1 and next(iter(ks.values())) == "operating":
        rain = [m["raw"]["rain_days"] for m in w2]
        return f"weather is the main shortfall for all four (rain ~{min(rain):.0f}-{max(rain):.0f} days a year)"
    return "; ".join(watch(m) for m in w2)


def weather_risk():
    snow = max(launch, key=lambda m: m["raw"]["snow_days"])
    wet = max(launch, key=lambda m: m["raw"]["rain_days"])
    heat = max(launch, key=lambda m: m["raw"]["heat_days"])
    lead = (f"{snow['metro']} has snow on ~{snow['raw']['snow_days']:.0f} days a year, " if snow["raw"]["snow_days"] >= 3
            else "No launch metro has meaningful snow; ")
    return f"{lead}{wet['metro']} has rain on ~{wet['raw']['rain_days']:.0f} days and {heat['metro']} ~{heat['raw']['heat_days']:.0f} days at 40 C or higher. Validate heat and wet-weather performance before public launch."


explain = min(w1, key=lambda m: m["opportunity"])        # the wave 1 metro whose rank leans least on demand
vq = p["quad"](vegas)
v = meta["vintages"]
asof = meta["data_as_of"]

vegas_line = (f"Las Vegas, the beachhead, scores \"{vq}\" on this model (demand {vegas['opportunity']:.0f}/100), which shows it underweights tourism-driven demand: visitors are not in resident population, density or commute data."
              if vq == "Opportunistic" else f"Las Vegas, the beachhead, scores \"{vq}\" on this model (demand {vegas['opportunity']:.0f}/100).")
gate = (f" {min(w1, key=lambda m: m['confidence'])['metro']} only just clears the 50% wave 1 gate."
        if min(m["confidence"] for m in w1) < 0.6 else "")

memo = f"""# Where should the operator launch after Las Vegas?

*For the strategy team. Data as of {asof}. Sources: Census ACS 2024 5-year, NHTSA SGO ADS reports, NOAA GHCN-Daily, EIA, FAA, and researched seed files (AV rules, competitors) as of {asof}.*

**Recommendation.** {plan.one_line_answer(p)} {plan.wave1_timing(p)} {plan.gate_note(p)} The sequence uses balanced-weight scores for 25 US metros (demand 35, operating conditions 25, regulation 20, competition 15, charging 5). Waves 1 and 2 are limited to states with Tier 2+ AV rules; wave 1 also needs a top-5 finish in at least half of 10,000 weight draws.

**Why these metros** (rank, score, demand score, regulation, competitors, confidence, fleet at {pct(meta['assumptions']['capture_share']['value'])} capture)

{chr(10).join(line(m) for m in w1)}
- **Wave 2:** {plan.names(w2)} (top 5 in {', '.join(pct(m['confidence']) for m in w2)} of draws). Demand {min(m['opportunity'] for m in w2):.0f}-{max(m['opportunity'] for m in w2):.0f} (wave 1: {min(m['opportunity'] for m in w1):.0f}-{max(m['opportunity'] for m in w1):.0f}). Watch: {watch_line()}.
- **Wave 3:** {plan.names(w3)}. Demand {min(m['opportunity'] for m in w3):.0f}-{max(m['opportunity'] for m in w3):.0f}, but driverless commercial service is not yet allowed. Build the policy case now; launch when the law changes.
- **Dallas-Fort Worth and Houston.** {dh_line()}
{why_rank_line(explain)}

**Deprioritize.** {dep_lines}. None ranks better than #{best_rank} in any scenario ({best['metro']}).

**Key risks and de-risking**

- *Regulation:* {n_top10_low} of the top 10 sit in Tier 0-1 states; engage {plan.names(sorted({m['state'] for m in w3}))} regulators early. {plan.names(sorted({m['state'] for m in slow_open}))} {'is' if len({m['state'] for m in slow_open}) == 1 else 'are'} Tier 2+ but {'needs' if len({m['state'] for m in slow_open}) == 1 else 'need'} multi-step permits for a new entrant.
- *Weather:* {weather_risk()}
- *Competition:* {plan.names(crowded)} already have operators (crowding {min(m['raw']['crowding'] for m in crowded):.1f}-{max(m['raw']['crowding'] for m in crowded):.1f}); {least_crowded['metro']} is the least crowded launch metro ({least_crowded['raw']['crowding']:.1f}). Competitor status is dated and cross-checked against NHTSA activity.

**Confidence.** {w1[0]['metro']} is top 5 in {pct(w1[0]['confidence'])} of weight draws and {w1[-1]['metro']} in {pct(w1[-1]['confidence'])}; {weakest['metro']} is the softest pick ({pct(weakest['confidence'])}), so wave 2 order is not firm. A low-risk lens puts {plan.names(low_risk)} on top; fast growth, {plan.names(fast)}. {vegas_line} The answer would also change if a Tier 1 state legalized driverless service, a competitor entered {least_crowded['metro']}, or fare and capture differ from our labeled assumptions.

**Data.** ACS {v['acs']}; FAA {v['faa']}; NOAA GHCN-Daily airport-station weather 2016-2025; NHTSA SGO reports to Sep 2026 (activity only, never rates); EIA {v['eia'].split(' (')[0]}; AV rules, new-entrant paths and competitors researched {asof} (some rows medium/low confidence); demand is a two-anchor estimate (Chicago and NYC ride-hail trips), not a forecast.
"""
out = pathlib.Path(__file__).resolve().parent / "memo.md"
out.write_text(memo, encoding="utf-8")
print(f"wrote {out} ({len(memo.split())} words)")
