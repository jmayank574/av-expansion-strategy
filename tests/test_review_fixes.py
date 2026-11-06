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


def test_memo_explains_detroit_rank(memo):
    d = plan.build()["by"]["Detroit"]
    assert f"**Why Detroit is #{d['ranks']['balanced']}:**" in memo and "competition (+" in memo
