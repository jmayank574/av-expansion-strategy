"""Guards for the review fixes: competitor seed, new-entrant regulation, unit-economics framing, deck and memo polish."""
import json, pathlib, shutil, sys
import pandas as pd, pytest, yaml
from pptx import Presentation

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plan

SRC = ["source_url", "source_title", "as_of_date", "confidence"]


def test_competitor_seed_covers_all_26_metros_and_is_sourced():
    comp = pd.read_csv(ROOT / "data/seed/competitor_presence.csv", dtype=str, keep_default_na=False)
    metros = {m["name"] for m in yaml.safe_load(open(ROOT / "config/metros.yaml"))["metros"]}
    assert metros <= set(comp.metro)
    assert bool((comp[SRC] != "").all().all())


def test_crosscheck_has_no_operator_missing_from_seed():
    xc = pd.read_csv(ROOT / "data/interim/crosscheck.csv", dtype=str, keep_default_na=False)
    assert (xc.nhtsa_not_in_seed == "-").all(), xc[xc.nhtsa_not_in_seed != "-"][["metro", "nhtsa_not_in_seed"]]


def test_new_entrant_path_is_sourced_for_every_state():
    reg = pd.read_csv(ROOT / "data/seed/state_av_regulation.csv", dtype=str, keep_default_na=False)
    assert reg.new_entrant_path.isin(["fast", "moderate", "slow"]).all()
    need = ["new_entrant_rationale", "new_entrant_source_url", "new_entrant_source_title", "new_entrant_as_of_date", "new_entrant_confidence"]
    assert bool((reg[need] != "").all().all())


def test_regulatory_pillar_is_60_tier_40_path_and_other_weights_unchanged():
    cfg = yaml.safe_load(open(ROOT / "config/weights.yaml"))
    reg = cfg["pillars"]["regulatory"]["submetrics"]
    assert {k: v["weight"] for k, v in reg.items()} == {"reg_tier": 60, "new_entrant_score": 40}
    assert cfg["scenarios"]["balanced"] == {"demand": 35, "operating": 25, "regulatory": 20, "competition": 15, "charging": 5}
    assert {k: v["weight"] for k, v in cfg["pillars"]["demand"]["submetrics"].items()} == {
        "log_metro_pop": 30, "city_density": 25, "taxi_ridehail_share": 20, "no_vehicle_share": 15, "enplanements_per_resident": 10}


def test_json_carries_new_entrant_fields():
    d = json.load(open(ROOT / "data/output/metros_scored.json"))
    for m in d["metros"]:
        assert m["regulation"]["new_entrant_path"] in ("fast", "moderate", "slow")
        assert "new_entrant_score" in m["sub_scores"]


@pytest.fixture(scope="module")
def memo():
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "reports/make_memo.py")], check=True, capture_output=True)
    return (ROOT / "reports/memo.md").read_text(encoding="utf-8")


def test_memo_lists_are_preceded_by_a_blank_line(memo):
    lines = memo.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("- ") and i > 0 and not lines[i - 1].startswith("- "):
            assert lines[i - 1] == "", f"list at line {i + 1} would not render as bullets"


def test_memo_content_requirements(memo):
    p = plan.build()
    assert "Dallas-Fort Worth ranks #" in memo and "Houston ranks #" in memo
    assert "Las Vegas, the beachhead, scores" in memo and "underweights tourism-driven demand" in memo
    for m in p["w1"]:
        if m["ease_of_entry"] < p["med_ease"]:
            assert "Left of the ease median" in memo
    assert "metros_scored.json" not in memo and "docs/methodology.md" not in memo
    assert "Census ACS 2024 5-year" in memo and "NHTSA SGO" in memo


def test_memo_renders_bullets_and_fits_one_page():
    import render_memo
    if not any(pathlib.Path(b).exists() or shutil.which(b) for b in render_memo.BROWSERS):
        pytest.skip("no Edge/Chrome available to print the PDF")
    assert render_memo.render()


def test_deck_title_labels_and_footers():
    p = plan.build()
    prs = Presentation(ROOT / "reports/deck.pptx")
    texts = [[sh.text_frame.text for sh in s.shapes if sh.has_text_frame] for s in prs.slides]
    assert plan.names(p["w1"]) in " ".join(texts[2][:2])                       # slide 3 title lists wave 1
    for i, t in enumerate(texts[1:], start=2):
        foot = " ".join(t)
        assert "metros_scored.json" not in foot and "Census ACS 2024 5-year" in foot, f"slide {i}"
    s5 = " ".join(texts[4])
    assert "annual revenue pool" in s5 and "assumption-driven" in s5 and "50 years" not in s5


def test_memo_explains_the_wave1_metro_that_leans_least_on_demand(memo):
    p = plan.build()
    m = min(p["w1"], key=lambda x: x["opportunity"])
    assert f"**Why {m['metro']} is #{m['ranks']['balanced']}:**" in memo


def test_memo_says_which_wave_dallas_and_houston_are_in(memo):
    p = plan.build()
    for name in ("Dallas-Fort Worth", "Houston"):
        m = p["by"][name]
        wv = next((w for w, ws in (("wave 1", p["w1"]), ("wave 2", p["w2"]), ("wave 3", p["w3"])) if m in ws), None)
        assert f"{name} ranks #{m['ranks']['balanced']} of 25" in memo
        assert (f"It is in {wv}." if wv else "It is in no wave.") in memo


def test_operator_presence_is_not_competition_and_is_not_named_in_outputs():
    comp = pd.read_csv(ROOT / "data/seed/competitor_presence.csv", dtype=str, keep_default_na=False)
    op = comp[comp.is_operator == "true"]
    assert len(op) >= 1 and set(comp.is_operator) <= {"true", "false"}
    w = yaml.safe_load(open(ROOT / "config/weights.yaml"))["crowding_status_weights"]
    d = json.load(open(ROOT / "data/output/metros_scored.json"))
    for m in d["metros"]:
        expect = sum(w[c.status] for c in comp[(comp.metro == m["metro"]) & (comp.is_operator == "false")].itertuples())
        assert abs(m["raw"]["crowding"] - expect) < 1e-6, m["metro"]
    assert "Motional" not in json.dumps(d)                 # ground rule 6: the operator is never named in app data
    assert "Motional" not in (ROOT / "reports/memo.md").read_text(encoding="utf-8")


def test_crowding_is_min_max_scaled_and_other_metrics_stay_percentile():
    import score
    cfg = yaml.safe_load(open(ROOT / "config/weights.yaml"))
    norm = {s: v.get("normalization", "percentile") for p in cfg["pillars"].values() for s, v in p["submetrics"].items()}
    assert norm["crowding"] == "minmax0" and all(v == "percentile" for k, v in norm.items() if k != "crowding")
    f = pd.read_parquet(ROOT / "data/interim/features.parquet").reset_index(drop=True)
    sub = score.sub_scores(f)
    cand = ~f.benchmark
    mx = f.crowding[cand].max()
    assert sub.crowding[f.crowding == 0].eq(100).all()
    assert abs(sub.crowding[cand][f.crowding[cand] == mx].iloc[0]) < 1e-9
    assert (sub.crowding[cand] - (100 - f.crowding[cand] / mx * 100)).abs().max() < 1e-9      # linear in crowding


def test_weather_uses_noaa_stations_with_station_ids_in_metros_yaml():
    metros = yaml.safe_load(open(ROOT / "config/metros.yaml"))["metros"]
    assert all(m["weather_station"].startswith("USW") for m in metros)
    w = pd.read_parquet(ROOT / "data/interim/weather.parquet")
    assert len(w) == 26 and (w.days == 3653).all()
    src = w[w.weather_source.str.startswith("NOAA")]
    assert (src.missing_pct <= 5).all()
    assert (w[~w.weather_source.str.startswith("NOAA")].missing_pct > 5).all()      # fallback only when a station is over 5% missing


def test_chicago_waymo_is_testing_and_citations_fixed():
    comp = pd.read_csv(ROOT / "data/seed/competitor_presence.csv", dtype=str, keep_default_na=False)
    row = comp[(comp.metro == "Chicago") & (comp.competitor == "Waymo")].iloc[0]
    assert row.status == "testing" and "abc7chicago.com" in row.source_url
    reg = pd.read_csv(ROOT / "data/seed/state_av_regulation.csv", dtype=str, keep_default_na=False).set_index("state")
    assert "cleantechnica.com/2026/02/20" in reg.at["NY", "source_url"] and "cleantechnica.com/2026/02/20" in reg.at["NY", "new_entrant_source_url"]
    assert "phillyvoice.com" in reg.at["PA", "source_url"]


def test_assumption_references_added_and_values_unchanged():
    a = yaml.safe_load(open(ROOT / "config/assumptions.yaml"))["assumptions"]
    assert "techcrunch.com" in a["avg_fare_usd"]["source_url"] and "PREMIUM" in a["avg_fare_usd"]["rationale"]
    assert "thenextweb.com" in a["vehicle_cost_usd"]["source_url"]
    assert "softwareseni.com" in a["cost_per_mile_usd"]["source_url"] and "newsroom.aaa.com" in a["cost_per_mile_usd"]["source_url"]
    assert (a["avg_fare_usd"]["value"], a["vehicle_cost_usd"]["value"], a["cost_per_mile_usd"]["value"]) == (20.0, 140000, 1.10)


def test_json_stamps_waves_for_the_app():
    d = json.load(open(ROOT / "data/output/metros_scored.json"))
    p = plan.build(d)
    stamped = {m["metro"]: m["wave"] for m in d["metros"] if m.get("wave")}
    assert stamped == {m["metro"]: w for w, ms in ((1, p["w1"]), (2, p["w2"]), (3, p["w3"])) for m in ms}
    assert all(m.get("wave") is None for m in d["metros"] if m["benchmark"])


def test_memo_and_deck_say_slow_permit_wave1_metros_start_permits_first(memo):
    p = plan.build()
    first, slow = plan.wave1_split(p)
    assert slow, "this check assumes at least one wave 1 metro in a slow-path state"
    assert plan.wave1_timing(p) in memo
    gate = plan.gate_note(p)
    if gate:
        assert gate in memo
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "reports/make_deck.py")], check=True, capture_output=True)
    prs = Presentation(ROOT / "reports/deck.pptx")
    s4 = " ".join(sh.text_frame.text for sh in prs.slides[3].shapes if sh.has_text_frame)
    assert "launches first" in s4 and "permits now, paid service after" in s4
    for m in first + slow:
        assert m["metro"] in s4
    if gate:
        assert "only just clears the 50% gate" in s4


def _slide_text(prs, i, notes=False):
    s = prs.slides[i]
    t = " ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
    return (t + " " + s.notes_slide.notes_text_frame.text) if notes else t


def test_slide5_contains_only_wave1_metros():
    p = plan.build()
    prs = Presentation(ROOT / "reports/deck.pptx")
    w1 = [m["metro"] for m in p["w1"]]
    text = _slide_text(prs, 4, notes=True)
    notes = prs.slides[4].notes_slide.notes_text_frame.text
    assert sorted(notes.split(": ", 1)[1].split(", ")) == sorted(w1)          # the chart's metro list is recorded in the notes
    for m in p["cand"]:
        if m["metro"] not in w1:
            assert m["metro"] not in text, f"{m['metro']} is not wave 1 but appears on slide 5"
    assert "principal-city launch area, not the whole metro" in text and "Wave 1 needs" in text


def test_slide6_weather_row_lists_only_meaningful_values_and_competition_wording():
    p = plan.build()
    prs = Presentation(ROOT / "reports/deck.pptx")
    t = _slide_text(prs, 5)
    risks = plan.weather_risks(p)
    assert risks and all(v >= plan.RISK_THRESHOLD[k] for k, hits in risks.items() for _, v in hits)
    for k, hits in risks.items():
        assert all(m in t for m, _ in hits)
    import re
    assert not re.search(r"~0\b|\b0 days", t)                                 # never list a zero value as a risk
    weather_row = t.split("Weather")[1].split("Competition")[0]
    launch = {m["metro"] for m in p["w1"] + p["w2"]}
    assert all(m["metro"] in launch for m in p["cand"] if m["metro"] in weather_row), "weather evidence must come from wave 1 and 2 metros only"
    assert "fewest operators" in t and "least crowded" not in t
    assert "storm and heavy-rain validation" in t.lower() and "heat validation" in t.lower()


def test_slides_2_and_7_state_normalization_references_and_validation():
    prs = Presentation(ROOT / "reports/deck.pptx")
    assert "except competitor crowding, which is min-max scaled" in _slide_text(prs, 1)
    s7 = _slide_text(prs, 6)
    assert "except competitor crowding (min-max scaled)" in s7
    assert "benchmarked to public references (Obi fares, Morgan Stanley vehicle cost, AAA operating cost)" in s7
    assert "Inputs validated against Census estimates, NYC TLC and Chicago trip data" in s7 and "docs/validation.md" in s7


def test_memo_unit_economics_line_says_principal_city(memo):
    assert "principal-city ride-hail trips, not the whole metro" in memo
