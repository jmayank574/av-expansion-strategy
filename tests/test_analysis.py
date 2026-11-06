import json, sys, pathlib
import numpy as np, pandas as pd, pytest, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import monte_carlo, unit_economics
import score
from common import INTERIM

A = yaml.safe_load(open(ROOT / "config/assumptions.yaml"))["assumptions"]


def test_every_assumption_is_sourced_or_labeled():
    for k, v in A.items():
        assert {"value", "low", "high", "source_url", "rationale", "label"} <= set(v), k
        assert v["source_url"], k
        assert v["rationale"].strip(), k


def test_assumption_ranges_are_ordered_pessimistic_to_optimistic():
    for k, v in A.items():
        if v["higher_is_better"]:
            assert v["low"] <= v["value"] <= v["high"], k
        else:
            assert v["low"] >= v["value"] >= v["high"], k


def test_demand_calibration_reproduces_anchors():
    d = pd.read_parquet(INTERIM / "demand.parquet").set_index("metro")
    for m in ("Chicago", "New York"):
        assert d.tpr_low[m] == d.tpr_base[m] == d.tpr_high[m]
    assert (d.tpr_low <= d.tpr_base + 1e-9).all() and (d.tpr_base <= d.tpr_high + 1e-9).all()


def test_unit_economics_hand_calculation():
    a = {k: v["value"] for k, v in A.items()}
    e = unit_economics.economics(10_000_000, 12.0, a)
    trips_day = 10_000_000 * a["capture_share"] / 365
    assert e["addressable_trips_per_day"] == pytest.approx(trips_day)
    assert e["fleet_vehicles"] == pytest.approx(trips_day / a["trips_per_vehicle_per_day"])
    miles = a["trips_per_vehicle_per_day"] * 365 * a["avg_trip_miles"] / (1 - a["deadhead_share"])
    opex = miles * a["cost_per_mile_usd"] + miles * a["kwh_per_mile"] * 0.12
    rev = a["trips_per_vehicle_per_day"] * 365 * a["avg_fare_usd"]
    assert e["contribution_per_vehicle"] == pytest.approx(rev - opex)
    assert e["payback_years"] == pytest.approx(a["vehicle_cost_usd"] / (rev - opex))


def test_payback_is_none_when_contribution_not_positive():
    a = {k: v["value"] for k, v in A.items()}
    a["avg_fare_usd"] = 0.5
    assert unit_economics.economics(1e7, 12.0, a)["payback_years"] is None


def test_monte_carlo_is_seeded_and_reproducible():
    f = pd.read_parquet(INTERIM / "features.parquet").reset_index(drop=True)
    pill = score.pillar_scores(score.sub_scores(f))
    pill.index = f.metro
    cand = pill[~f.benchmark.values]
    bw = score.CFG["scenarios"]["balanced"]
    r1 = monte_carlo.run(cand, bw, draws=2000)
    r2 = monte_carlo.run(cand, bw, draws=2000)
    pd.testing.assert_frame_equal(r1, r2)
    assert r1.top_n_share.sum() == pytest.approx(5, abs=0.1)
    assert r1.top_n_share.between(0, 1).all()
    r3 = monte_carlo.run(cand, bw, draws=2000, seed=7)
    assert not r1.top_n_share.equals(r3.top_n_share)


def test_json_contains_phase3_fields():
    d = json.load(open(ROOT / "data/output/metros_scored.json"))
    for m in d["metros"]:
        assert set(m["unit_economics"]) == {"low", "base", "high"}
        assert "demand_estimate" in m
        if not m["benchmark"]:
            assert 0 <= m["confidence"] <= 1
    assert "assumptions" in d["meta"]
