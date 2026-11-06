"""Unit economics per metro. Inputs only from config/assumptions.yaml plus the EIA commercial price and the demand estimate."""
import sys, pathlib, yaml, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))
from common import *

A = yaml.safe_load(open(ROOT / "config/assumptions.yaml"))["assumptions"]
CASES = {"low": "low", "base": "value", "high": "high"}   # low = pessimistic end of every input, high = optimistic end


def economics(trips_year: float, elec_cents_kwh: float, a: dict) -> dict:
    """a: dict of assumption name -> number. All outputs are annual unless named otherwise."""
    trips_day = trips_year * a["capture_share"] / 365                      # addressable robotaxi trips per day
    fleet = trips_day / a["trips_per_vehicle_per_day"]                     # vehicles needed
    veh_trips = a["trips_per_vehicle_per_day"] * 365
    revenue = veh_trips * a["avg_fare_usd"]                                # per vehicle per year
    miles = veh_trips * a["avg_trip_miles"] / (1 - a["deadhead_share"])    # total vehicle miles per year
    charging = miles * a["kwh_per_mile"] * elec_cents_kwh / 100
    opex = miles * a["cost_per_mile_usd"] + charging
    contribution = revenue - opex
    payback = a["vehicle_cost_usd"] / contribution if contribution > 0 else None
    return dict(addressable_trips_per_day=trips_day, fleet_vehicles=fleet, revenue_per_vehicle=revenue, miles_per_vehicle=miles,
                charging_cost_per_vehicle=charging, opex_per_vehicle=opex, contribution_per_vehicle=contribution, payback_years=payback)


def case_inputs(case: str) -> dict:
    return {k: v[CASES[case]] for k, v in A.items()}


def main():
    d = pd.read_parquet(INTERIM / "demand.parquet")
    feats = pd.read_parquet(INTERIM / "features.parquet")[["metro", "elec_cents_kwh"]]
    d = d.merge(feats, on="metro")
    rows = []
    for _, r in d.iterrows():
        for case in CASES:
            e = economics(r[f"trips_{case}"], r.elec_cents_kwh, case_inputs(case))
            rows.append(dict(metro=r.metro, case=case, city_ride_hail_trips_year=r[f"trips_{case}"], **e))
    ue = pd.DataFrame(rows)
    ue.to_parquet(INTERIM / "unit_economics.parquet", index=False)
    b = ue[ue.case == "base"].set_index("metro")
    # sanity: hand-computed base case for one metro
    r = d.set_index("metro").loc["Phoenix"]; a = case_inputs("base")
    trips_day = r.trips_base * a["capture_share"] / 365
    miles = a["trips_per_vehicle_per_day"] * 365 * a["avg_trip_miles"] / (1 - a["deadhead_share"])
    contrib = a["trips_per_vehicle_per_day"] * 365 * a["avg_fare_usd"] - miles * (a["cost_per_mile_usd"] + a["kwh_per_mile"] * r.elec_cents_kwh / 100)
    extra = "\n".join([
        "Cases: low = pessimistic end of every input and the low demand estimate; base = central values; high = optimistic end and the high demand estimate.",
        "Revenue, cost and payback per vehicle do not depend on demand; demand only sets the fleet size.", "",
        "## Base case, all candidates", b.reset_index()[["metro", "addressable_trips_per_day", "fleet_vehicles", "revenue_per_vehicle", "opex_per_vehicle",
        "contribution_per_vehicle", "payback_years"]].round(1).to_markdown(index=False),
        "", "## Assumptions", pd.DataFrame(A).T[["value", "low", "high", "source_url"]].to_markdown()])
    ok = write_profile("11_unit_economics", ue, [
        ("every assumption has value, low, high, source_url and rationale", all({"value", "low", "high", "source_url", "rationale"} <= set(v) for v in A.values())),
        ("every assumption is sourced or labeled", all(v["source_url"] for v in A.values())),
        ("base case matches a hand calculation (Phoenix)", abs(b.fleet_vehicles["Phoenix"] - trips_day / a["trips_per_vehicle_per_day"]) < 1e-6 and abs(b.contribution_per_vehicle["Phoenix"] - contrib) < 1e-6),
        ("low <= base <= high contribution per vehicle for every metro", all(
            ue[(ue.metro == m)].set_index("case").contribution_per_vehicle[["low", "base", "high"]].is_monotonic_increasing for m in ue.metro.unique())),
        ("base payback between 0.5 and 10 years", bool(b.payback_years.between(0.5, 10).all())),
        ("no negative fleets", bool((ue.fleet_vehicles >= 0).all()))], extra=extra)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
