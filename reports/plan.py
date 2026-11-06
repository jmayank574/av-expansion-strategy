"""Launch plan derived from data/output/metros_scored.json. Shared by the memo and the deck so every number traces to the JSON.

Rules (documented in docs/methodology.md):
  Wave 1: balanced top 5, regulation tier >= 2, top-5 in >= 50% of Monte Carlo weight draws
  Wave 2: remaining metros ranked 1-10 (balanced) in tier >= 2 states
  Wave 3: remaining metros ranked 1-10 in tier 0-1 states (policy-dependent, build the case)
  Deprioritize: balanced rank >= 18
"""
import json, pathlib, statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load():
    return json.load(open(ROOT / "data/output/metros_scored.json"))


def build(d=None):
    d = d or load()
    cand = [m for m in d["metros"] if not m["benchmark"]]
    rank = lambda m: m["ranks"]["balanced"]
    by = {m["metro"]: m for m in cand}
    cand.sort(key=lambda m: (rank(m), -m["total"], m["metro"]))
    tier = lambda m: m["regulation"]["tier"]
    w1 = [m for m in cand if rank(m) <= 5 and tier(m) >= 2 and (m["confidence"] or 0) >= 0.5]
    used = {m["metro"] for m in w1}
    w2 = [m for m in cand if rank(m) <= 10 and tier(m) >= 2 and m["metro"] not in used]
    used |= {m["metro"] for m in w2}
    w3 = [m for m in cand if rank(m) <= 10 and tier(m) <= 1 and m["metro"] not in used]
    used |= {m["metro"] for m in w3}
    depri = [m for m in cand if rank(m) >= 18]
    watch = [m for m in cand if m["metro"] not in used and m not in depri]
    mx = statistics.median(m["ease_of_entry"] for m in cand)
    my = statistics.median(m["opportunity"] for m in cand)
    quad = lambda m: ("Launch next" if m["ease_of_entry"] >= mx else "Build case") if m["opportunity"] >= my else ("Opportunistic" if m["ease_of_entry"] >= mx else "Deprioritize")
    top5 = {k: [m["metro"] for m in sorted(cand, key=lambda m: (m["ranks"][k], m["metro"]))][:5] for k in d["meta"]["weights"]["scenarios"]}
    return dict(d=d, cand=cand, by=by, w1=w1, w2=w2, w3=w3, depri=depri, watch=watch, med_ease=mx, med_opp=my, quad=quad, top5=top5)


def names(ms):
    ms = [m["metro"] if isinstance(m, dict) else m for m in ms]
    return ms[0] if len(ms) == 1 else ", ".join(ms[:-1]) + " and " + ms[-1]


def fleet(m, case="base"):
    return m["unit_economics"][case]["fleet_vehicles"]


def one_line_answer(p):
    return (f"Enter {names(p['w1'])} first, then {names(p['w2'])}; hold {names(p['w3'])} until the rules change.")


# ---- shared wording helpers (memo and deck) -------------------------------------------------
SOURCES = "Census ACS 2024 5-year, NHTSA SGO ADS reports, Open-Meteo, EIA, FAA, researched seed files (AV rules, competitors)"


def sources_line(meta):
    """Footer text naming real sources instead of a file path."""
    return f"Sources: Census ACS 2024 5-year, NHTSA SGO, Open-Meteo, EIA, FAA, researched seed files as of {meta['data_as_of']}"


def operating(m):
    return [c["competitor"] for c in m["competitors"] if c["status"] in ("operating_public", "operating_limited") and not c.get("is_operator")]


PATH_TXT = {"fast": "fast", "moderate": "moderate", "slow": "slow"}


def weak_phrase(pillar, m, crowd_rank=None, n=25, med_opp=50.8):
    r = m["raw"]
    if pillar == "competition":
        ops = operating(m)
        rk = "the most crowded field of " + str(n) if crowd_rank == 1 else (f"the #{crowd_rank} most crowded field of {n}" if crowd_rank and crowd_rank <= 5 else "a crowded field")
        return f"{rk} (crowding {r['crowding']:.1f}" + (f"; {names(ops)} operating)" if ops else ")")
    if pillar == "regulatory":
        return f"a {m['regulation']['new_entrant_path']} new-entrant path in {m['state']} (Tier {m['regulation']['tier']})"
    if pillar == "operating":
        return f"weather (rain ~{r['rain_days']:.0f}, snow ~{r['snow_days']:.0f}, 40 C+ ~{r['heat_days']:.0f} days a year)"
    if pillar == "demand":
        return f"{'middling' if abs(m['opportunity'] - med_opp) < 10 else 'modest'} demand ({m['opportunity']:.0f}/100)"
    return f"a {r['elec_cents_kwh']:.0f} cent/kWh power price"


def shortfalls(m, pillars):
    """Pillars ranked by weighted shortfall from 100 under the balanced weights."""
    w = m_weights(m)
    return sorted(pillars, key=lambda k: -(100 - m["pillar_scores"][k]) * w[k])


_W = {}


def m_weights(_m):
    return _W["w"]


def set_weights(meta):
    _W["w"] = meta["weights"]["scenarios"][meta["weights"]["default_scenario"]]


def left_of_ease_median_reason(m, med):
    a, b = shortfalls(m, ["regulatory", "operating", "competition", "charging"])[:2]
    return f"Left of the ease median ({m['ease_of_entry']:.0f} vs {med:.0f}) because of {weak_phrase(a, m)} and {weak_phrase(b, m)}."


def why_rank(m, cand, med_opp=50.8):
    """One sentence on where a metro ranks and why (for metros the reader will ask about)."""
    n = len(cand)
    crowd_rank = 1 + sum(1 for x in cand if x["raw"]["crowding"] > m["raw"]["crowding"])
    pills = ["demand", "operating", "regulatory", "competition", "charging"]
    good = [k for k in pills if k != "charging" and m["pillar_scores"][k] >= 65]      # charging is 5% of the score: not worth citing
    strong = max(good, key=lambda k: m["pillar_scores"][k] * m_weights(m)[k]) if good else max(pills, key=lambda k: m["pillar_scores"][k] * m_weights(m)[k])
    weak = shortfalls(m, [k for k in pills if k != strong])[:2]
    sfx = {"regulatory": f"Tier {m['regulation']['tier']} rules with a {m['regulation']['new_entrant_path']} new-entrant path",
           "demand": f"strong demand ({m['opportunity']:.0f}/100)", "operating": "good operating conditions",
           "competition": "a light competitive field", "charging": "cheap power"}[strong]
    w = [weak_phrase(k, m, crowd_rank, n, med_opp) for k in weak]
    return f"{m['metro']} ranks #{m['ranks']['balanced']} of {n} ({m['total']:.1f}): {sfx}, held back by {w[0]} and {w[1]}."
