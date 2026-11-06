"""Monte Carlo on pillar weights: 10,000 Dirichlet draws centered on the balanced weights (seeded)."""
import sys, pathlib, yaml, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))
from common import *
import score

MC = yaml.safe_load(open(ROOT / "config/assumptions.yaml"))["monte_carlo"]


def run(pillars: pd.DataFrame, base_weights: dict, draws=MC["draws"], seed=MC["seed"], conc=MC["concentration"], top_n=MC["top_n"]) -> pd.DataFrame:
    """pillars: candidates only, columns = pillar names. Returns per-metro top-N share and median rank."""
    rng = np.random.default_rng(seed)
    w0 = np.array([base_weights[p] for p in pillars.columns], float)
    w0 /= w0.sum()
    W = rng.dirichlet(w0 * conc, size=draws)                       # draws x pillars, rows sum to 1
    T = np.round(W @ pillars.to_numpy().T, 9)                      # draws x metros
    ranks = (T[:, :, None] < T[:, None, :]).sum(axis=2) + 1        # rank 1 = best; ties share the best rank
    return pd.DataFrame({"metro": pillars.index, "top_n_share": (ranks <= top_n).mean(axis=0), "median_rank": np.median(ranks, axis=0),
                         "p10_rank": np.percentile(ranks, 10, axis=0), "p90_rank": np.percentile(ranks, 90, axis=0)})


def main():
    f = pd.read_parquet(INTERIM / "features.parquet").reset_index(drop=True)
    pill = score.pillar_scores(score.sub_scores(f))
    pill.index = f.metro
    cand = pill[~f.benchmark.values]
    bw = score.CFG["scenarios"][score.CFG["default_scenario"]]
    res = run(cand, bw)
    res2 = run(cand, bw)
    res.to_parquet(INTERIM / "monte_carlo.parquet", index=False)
    det = score.total_score(cand, bw).round(9).rank(ascending=False, method="min")
    top = res.sort_values("top_n_share", ascending=False)
    W = np.random.default_rng(MC["seed"]).dirichlet(np.array([bw[p] for p in cand.columns], float) / 100 * MC["concentration"], size=MC["draws"])
    extra = "\n".join([
        f"{MC['draws']:,} Dirichlet draws, seed {MC['seed']}, concentration {MC['concentration']} around the balanced weights {bw}.",
        "Mean drawn weights: " + ", ".join(f"{p} {100 * W[:, i].mean():.1f}" for i, p in enumerate(cand.columns)) +
        "; std: " + ", ".join(f"{p} {100 * W[:, i].std():.1f}" for i, p in enumerate(cand.columns)), "",
        "## Share of draws in the top 5 and median rank", top.assign(top5_share=lambda z: (z.top_n_share * 100).round(1), deterministic_rank=lambda z: z.metro.map(det))
        [["metro", "top5_share", "median_rank", "p10_rank", "p90_rank", "deterministic_rank"]].to_markdown(index=False)])
    t5 = set(det[det <= 5].index)
    ok = write_profile("12_monte_carlo", res, [
        ("reproducible: two runs with the same seed are identical", res.equals(res2)),
        ("top-5 shares sum to 5 (five metros in each draw, barring ties)", abs(res.top_n_share.sum() - 5) < 0.05),
        ("mean drawn weights are within 1 point of the balanced weights", all(abs(100 * W[:, i].mean() - bw[p]) < 1 for i, p in enumerate(cand.columns))),
        ("every deterministic top-5 metro is in the top 10 by Monte Carlo share", t5 <= set(top.metro.head(10)))], extra=extra)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
