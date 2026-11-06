"""Percentile-rank normalization, pillar/total scores, scenarios, Vegas similarity, why-bullets -> data/output/metros_scored.json."""
import json, datetime, numpy as np, pandas as pd, yaml
from common import *

CFG = yaml.safe_load(open(ROOT / "config/weights.yaml"))
PILLARS = list(CFG["pillars"])
SUBS = {p: CFG["pillars"][p]["submetrics"] for p in PILLARS}
ALL_SUBS = [s for p in PILLARS for s in SUBS[p]]
SIM_FEATURES = ["rain_days", "snow_days", "heat_days", "city_density", "enplanements_per_resident"]


def percentile_map(cand_values: pd.Series):
    """Map raw value -> 0..100 percentile using average ranks across the candidates (min=0, max=100)."""
    r = cand_values.rank(method="average")
    pct = (r - 1) / (len(cand_values) - 1) * 100
    tbl = pd.DataFrame({"v": cand_values.values, "p": pct.values}).groupby("v", as_index=False).p.mean().sort_values("v")
    return lambda x: np.interp(x, tbl.v.values, tbl.p.values)   # benchmark is interpolated, never ranked


def sub_scores(f: pd.DataFrame) -> pd.DataFrame:
    cand = f[~f.benchmark]
    out = pd.DataFrame(index=f.index)
    for p in PILLARS:
        for s, spec in SUBS[p].items():
            sc = percentile_map(cand[s])(f[s])
            out[s] = sc if spec["direction"] == 1 else 100 - sc
    return out


def pillar_scores(sub: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=sub.index)
    for p in PILLARS:
        w = pd.Series({s: v["weight"] for s, v in SUBS[p].items()})
        out[p] = (sub[w.index] * w).sum(axis=1) / w.sum()
    return out


def total_score(pill: pd.DataFrame, weights: dict) -> pd.Series:
    w = pd.Series(weights)[PILLARS]
    return (pill[PILLARS] * w).sum(axis=1) / w.sum()


def ease_of_entry(pill: pd.DataFrame, weights: dict) -> pd.Series:
    w = pd.Series({p: weights[p] for p in PILLARS if p != "demand"})
    return (pill[w.index] * w).sum(axis=1) / w.sum()


def vegas_similarity(f: pd.DataFrame) -> pd.Series:
    cand = f[~f.benchmark]
    mu, sd = cand[SIM_FEATURES].mean(), cand[SIM_FEATURES].std(ddof=0)
    z = (f[SIM_FEATURES] - mu) / sd
    zv = z[f.benchmark].iloc[0]
    d = np.sqrt(((z - zv) ** 2).sum(axis=1))
    return 100 - d / d[~f.benchmark].max() * 100


TIER_TXT = {3: "driverless commercial service allowed and operating", 2: "driverless deployment allowed with a permit or filing process",
            1: "testing only, driverless commercial service not yet allowed", 0: "restrictive, no legal pathway"}


def why_bullets(r, pill, sub, weights, active_comp):
    strengths = (pill * pd.Series(weights)[pill.index]).sort_values(ascending=False).index.tolist()[:2]   # by weighted contribution
    def strong(p):
        if p == "demand": return f"Demand score {pill['demand']:.0f}/100: {r.metro_pop/1e6:.1f}M-person metro, {r.city_density:,.0f} people per sq mi in {r.principal_city}"
        if p == "operating": return f"Operating conditions score {pill['operating']:.0f}/100: ~{r.rain_days:.0f} rain, {r.snow_days:.0f} snow and {r.heat_days:.0f} extreme-heat days a year"
        if p == "regulatory": return f"{r.state} is regulation Tier {int(r.reg_tier)}: {TIER_TXT[int(r.reg_tier)]}"
        if p == "competition": return f"Light competition: {len(active_comp)} operator(s) in service, crowding score {r.crowding:.1f}"
        return f"Low commercial power price ({r.elec_cents_kwh:.1f} cents/kWh)"
    # biggest risk = largest weighted shortfall
    short = {p: (100 - pill[p]) * weights[p] for p in PILLARS if p not in strengths}   # a pillar shown as a strength is not repeated as the risk
    rp = max(short, key=short.get)
    if rp == "operating":
        worst = max(SUBS["operating"], key=lambda s: (100 - sub[s]) * SUBS["operating"][s]["weight"])
        risk = {"snow_days": f"Snow on ~{r.snow_days:.0f} days a year: needs winter validation before launch",
                "rain_days": f"Rain on ~{r.rain_days:.0f} days a year: needs wet-weather validation before launch",
                "heat_days": f"Extreme heat (40 C+) on ~{r.heat_days:.0f} days a year: needs thermal validation before launch"}[worst]
    elif rp == "regulatory":
        risk = f"{r.state} is regulation Tier {int(r.reg_tier)} ({TIER_TXT[int(r.reg_tier)]}): launch depends on policy change or permits"
    elif rp == "competition":
        risk = f"Crowded field: {', '.join(active_comp) or 'several operators'} already present (crowding {r.crowding:.1f})"
    elif rp == "demand":
        risk = f"Demand is the biggest gap to a perfect score ({pill['demand']:.0f}/100): {r.metro_pop/1e6:.1f}M metro, {r.city_density:,.0f} people per sq mi in {r.principal_city}"
    else:
        risk = f"Higher power cost ({r.elec_cents_kwh:.1f} cents/kWh commercial) raises charging expense"
    return [strong(p) for p in strengths] + [risk]


def main():
    f = pd.read_parquet(INTERIM / "features.parquet").reset_index(drop=True)
    sub = sub_scores(f)
    pill = pillar_scores(sub)
    scen = CFG["scenarios"]
    totals = {k: total_score(pill, w) for k, w in scen.items()}
    cand = ~f.benchmark
    ranks = {k: totals[k][cand].round(9).rank(ascending=False, method="min").astype(int) for k in scen}
    sim = vegas_similarity(f)
    ease = ease_of_entry(pill, scen[CFG["default_scenario"]])
    comp = pd.read_parquet(INTERIM / "competitors.parquet")
    reg = pd.read_parquet(INTERIM / "regulation.parquet").set_index("state")
    nh = pd.read_parquet(INTERIM / "nhtsa.parquet")
    bw = scen[CFG["default_scenario"]]
    metros = []
    for i, r in f.iterrows():
        cs = comp[comp.metro == r.metro].sort_values("status")
        active = cs[cs.status.isin(["operating_public", "operating_limited"])].competitor.tolist()
        rg = reg.loc[r.state]
        raw_keys = ["metro_pop", "city_pop", "city_density", "land_sqmi", "taxi_ridehail_share", "no_vehicle_share", "city_median_hh_income",
                    "enplanements", "enplanements_per_resident", "rain_days", "snow_days", "heat_days", "reg_tier", "crowding", "n_competitors", "elec_cents_kwh", "log_metro_pop"]
        metros.append(dict(
            metro=r.metro, state=r.state, principal_city=r.principal_city, benchmark=bool(r.benchmark),
            raw={k: float(r[k]) for k in raw_keys},
            sub_scores={s: float(sub.at[i, s]) for s in ALL_SUBS},
            pillar_scores={p: float(pill.at[i, p]) for p in PILLARS},
            total=float(totals[CFG["default_scenario"]][i]),
            totals={k: float(totals[k][i]) for k in scen},
            ranks={k: (int(ranks[k][i]) if cand[i] else None) for k in scen},
            opportunity=float(pill.at[i, "demand"]), ease_of_entry=float(ease[i]), vegas_similarity=float(sim[i]),
            why=why_bullets(r, pill.loc[i], sub.loc[i], bw, active),
            competitors=cs[["competitor", "status", "platform_partner", "first_public_date", "source_url", "source_title", "as_of_date", "confidence"]].to_dict("records"),
            regulation=dict(tier=int(rg.tier), driverless_commercial_allowed=rg.driverless_commercial_allowed, permit_body=rg.permit_body,
                            key_law_or_rule=rg.key_law_or_rule, notes=rg.notes, source_url=rg.source_url, source_title=rg.source_title,
                            as_of_date=rg.as_of_date, confidence=rg.confidence),
            nhtsa_incidents=nh[nh.metro == r.metro][["operating_entity", "ads_incidents"]].to_dict("records"),
        ))
    meta = dict(
        question="Which US metros should a Level 4 robotaxi operator enter after its Las Vegas beachhead, and in what order?",
        weights=dict(scenarios=scen, default_scenario=CFG["default_scenario"],
                     pillars={p: dict(label=CFG["pillars"][p]["label"], submetrics=SUBS[p]) for p in PILLARS},
                     crowding_status_weights=CFG["crowding_status_weights"]),
        vintages=dict(acs=f.acs_vintage.iloc[0], faa="CY2025 enplanements", weather="Open-Meteo daily archive 2016-2025",
                      nhtsa=pd.read_parquet(INTERIM / "nhtsa_incidents.parquet").shape[0] and "NHTSA SGO ADS reports, 24 months ending Sep 2026",
                      eia=pd.read_parquet(INTERIM / "eia.parquet").eia_period.iloc[0] + " (commercial, Table 5.6.B)",
                      regulation_and_competitors="seed CSVs researched 2026-11-05", gazetteer="Census Gazetteer 2025"),
        data_as_of="2026-11-05",
        generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    )
    OUT = ROOT / "data/output"
    OUT.mkdir(exist_ok=True)
    json.dump(dict(meta=meta, metros=metros), open(OUT / "metros_scored.json", "w"), indent=1)

    # ---- profile: top 10 per scenario and movement
    t = pd.DataFrame({"metro": f.metro[cand]}).assign(**{k: ranks[k] for k in scen})
    lines = []
    for k in scen:
        top = t.sort_values(k).head(10)
        lines += [f"### Top 10: {k} {dict(scen[k])}", top[["metro", k]].assign(total=[round(totals[k][f.index[f.metro == m][0]], 1) for m in top.metro]).to_markdown(index=False), ""]
    t["rank_range"] = t[list(scen)].max(axis=1) - t[list(scen)].min(axis=1)
    lines += ["### Movement between scenarios (max rank - min rank)", t.sort_values("rank_range", ascending=False).head(12).to_markdown(index=False)]
    lines += ["", "### Vegas benchmark (not ranked)", f"Total {totals['balanced'][~cand].iloc[0]:.1f}; pillars " + json.dumps({p: round(float(pill.loc[~cand, p].iloc[0]), 1) for p in PILLARS}),
              "", "### Most / least similar to Vegas", sim[cand].groupby(f.metro).first().sort_values(ascending=False).round(1).head(5).to_frame("sim").to_markdown(),
              sim[cand].groupby(f.metro).first().sort_values().round(1).head(3).to_frame("sim").to_markdown()]
    out = pd.DataFrame({"metro": f.metro, "total": totals["balanced"].round(2), **{p: pill[p].round(1) for p in PILLARS}})
    ok = write_profile("09_scores", out, [
        ("scores within 0-100", bool(sub.stack().between(0, 100).all() and pill.stack().between(0, 100).all() and all(t.between(0, 100).all() for t in totals.values()))),
        ("all scenario weight sets sum to 100", all(sum(w.values()) == 100 for w in scen.values())),
        ("sub-metric weights sum to 100 per pillar", all(sum(v["weight"] for v in SUBS[p].values()) == 100 for p in PILLARS)),
        ("25 candidates ranked in each scenario, Vegas unranked", all(ranks[k].min() == 1 for k in scen) and len(ranks["balanced"]) == 25),
        ("Phoenix or San Diego above Minneapolis on operating pillar", max(pill.at[f.index[f.metro == "Phoenix"][0], "operating"], pill.at[f.index[f.metro == "San Diego"][0], "operating"]) > pill.at[f.index[f.metro == "Minneapolis"][0], "operating"])],
        extra="\n".join(lines))
    print("\n".join(lines[:14]))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
