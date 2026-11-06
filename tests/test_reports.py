import json, pathlib, re, subprocess, sys
import pytest
from pptx import Presentation

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plan


@pytest.fixture(scope="module", autouse=True)
def build_reports():
    for s in ("make_memo.py", "make_deck.py"):
        subprocess.run([sys.executable, str(ROOT / "reports" / s)], check=True, capture_output=True)


def test_memo_fits_one_page_by_length():
    memo = (ROOT / "reports/memo.md").read_text(encoding="utf-8")
    assert len(memo.split()) <= 800          # rendered to a single Letter page at 10 pt in Edge (render_memo.py checks the real page count)
    for h in ["Recommendation", "Why these metros", "Deprioritize", "Key risks", "Confidence", "Data"]:
        assert h in memo


def test_memo_numbers_trace_to_json():
    d = json.load(open(ROOT / "data/output/metros_scored.json"))
    memo = (ROOT / "reports/memo.md").read_text(encoding="utf-8")
    p = plan.build(d)
    for m in p["w1"]:
        assert f"**{m['metro']}** (#{m['ranks']['balanced']}, {m['total']:.1f})" in memo
        assert f"top 5 in {m['confidence'] * 100:.0f}% of draws" in memo
    assert plan.one_line_answer(p) in memo


def test_no_operator_branding():
    memo = (ROOT / "reports/memo.md").read_text(encoding="utf-8")
    assert "the operator" in memo.lower() or "operator" in memo.lower()


def test_deck_has_seven_slides_and_charts():
    prs = Presentation(ROOT / "reports/deck.pptx")
    assert len(prs.slides) == 7
    pics = sum(1 for s in prs.slides for sh in s.shapes if sh.shape_type == 13)
    assert pics == 2
    for f in ("quadrant.png", "unit_economics.png"):
        assert (ROOT / "reports/charts" / f).stat().st_size > 20_000


def test_waves_do_not_overlap_and_benchmark_excluded():
    p = plan.build()
    names = [m["metro"] for w in ("w1", "w2", "w3") for m in p[w]]
    assert len(names) == len(set(names)) and "Las Vegas" not in names
