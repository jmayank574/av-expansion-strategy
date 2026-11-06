import json, pandas as pd, pytest, score
from common import INTERIM, ROOT

CFG = score.CFG


@pytest.fixture(scope="module")
def feats():
    return pd.read_parquet(INTERIM / "features.parquet").reset_index(drop=True)


def test_scenario_weights_sum_to_100():
    for k, w in CFG["scenarios"].items():
        assert sum(w.values()) == 100, k
        assert set(w) == set(score.PILLARS)


def test_submetric_weights_sum_to_100_per_pillar():
    for p in score.PILLARS:
        assert sum(v["weight"] for v in score.SUBS[p].values()) == 100, p


def test_scores_within_0_100(feats):
    sub = score.sub_scores(feats)
    pill = score.pillar_scores(sub)
    assert sub.stack().between(0, 100).all() and pill.stack().between(0, 100).all()
    for w in CFG["scenarios"].values():
        assert score.total_score(pill, w).between(0, 100).all()
    assert feats.assign(s=score.vegas_similarity(feats)).s.between(0, 100).all()


def test_deterministic(feats):
    a = score.pillar_scores(score.sub_scores(feats))
    b = score.pillar_scores(score.sub_scores(feats.copy()))
    pd.testing.assert_frame_equal(a, b)


def test_benchmark_is_not_ranked():
    d = json.load(open(ROOT / "data/output/metros_scored.json"))
    lv = [m for m in d["metros"] if m["benchmark"]]
    assert len(lv) == 1 and lv[0]["metro"] == "Las Vegas" and all(v is None for v in lv[0]["ranks"].values())
    ranked = [m for m in d["metros"] if not m["benchmark"]]
    assert len(ranked) == 25
    for k in CFG["scenarios"]:
        assert sorted(m["ranks"][k] for m in ranked)[0] == 1


def test_weather_only_weights_favor_phoenix_or_san_diego_over_minneapolis(feats):
    pill = score.pillar_scores(score.sub_scores(feats))
    t = score.total_score(pill, {p: (100 if p == "operating" else 0) for p in score.PILLARS})
    t.index = feats.metro
    assert max(t["Phoenix"], t["San Diego"]) > t["Minneapolis"]


def test_percentile_extremes(feats):
    cand = feats[~feats.benchmark]
    f = score.percentile_map(cand.city_density)
    assert f(cand.city_density.max()) == pytest.approx(100) and f(cand.city_density.min()) == pytest.approx(0)
