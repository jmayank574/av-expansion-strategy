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
