"""Demand calibration from two anchors: Chicago TNP trips and NYC HVFHV trips, calendar 2025.
Only aggregate queries are used: SoQL group-by counts (Chicago) and parquet-footer row counts (NYC, no trip rows downloaded)."""
import json, sys, pathlib, numpy as np, pandas as pd, requests
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))
from common import *

YEAR = 2025
CACHE = RAW / "demand"
CACHE.mkdir(exist_ok=True)


def chicago_trips():
    f = CACHE / f"chicago_tnp_{YEAR}.json"
    if not f.exists():
        for attempt in range(4):
            try:
                r = requests.get("https://data.cityofchicago.org/resource/6dvr-xwnh.json", timeout=290, params={
                    "$select": "date_extract_y(trip_start_timestamp) as y, count(*) as n", "$group": "y", "$order": "y",
                    "$where": f"trip_start_timestamp >= '{YEAR}-01-01T00:00:00' and trip_start_timestamp < '{YEAR + 1}-01-01T00:00:00'"})
                r.raise_for_status()
                break
            except requests.RequestException as e:
                print("Chicago SoQL retry", attempt + 1, type(e).__name__)
        else:
            raise SystemExit("Chicago TNP aggregate query failed after retries")
        f.write_text(r.text)
    return int(next(x["n"] for x in json.loads(f.read_text()) if int(x["y"]) == YEAR))


def nyc_trips():
    f = CACHE / f"nyc_hvfhv_{YEAR}.json"
    if not f.exists():
        import duckdb
        con = duckdb.connect()
        con.execute("install httpfs; load httpfs;")
        out = {f"{YEAR}-{m:02d}": con.execute(
            f"select count(*) from read_parquet('https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_{YEAR}-{m:02d}.parquet')").fetchone()[0]
            for m in range(1, 13)}
        f.write_text(json.dumps(out))
    d = json.loads(f.read_text())
    assert len(d) == 12
    return sum(d.values())


acs = pd.read_parquet(INTERIM / "acs.parquet")
gz = pd.read_parquet(INTERIM / "gazetteer.parquet")[["metro", "density_per_sqmi"]]
faa = pd.read_parquet(INTERIM / "faa.parquet")[["metro", "enplanements_per_resident"]]
d = acs[["metro", "city_pop", "taxi_ridehail_share", "no_vehicle_share"]].merge(gz, on="metro").merge(faa, on="metro")
# demand index = geometric mean of the four ACS/FAA indicators (scale cancels in ratios)
IND = ["density_per_sqmi", "taxi_ridehail_share", "no_vehicle_share", "enplanements_per_resident"]
d["demand_index"] = np.exp(np.log(d[IND]).mean(axis=1))

obs = {"Chicago": chicago_trips(), "New York": nyc_trips()}
a = d.set_index("metro")
tpr = {k: v / a.city_pop[k] for k, v in obs.items()}                # observed trips per principal-city resident
est = {k: tpr[k] * a.demand_index / a.demand_index[k] for k in obs}   # proportional scaling from each anchor
lo = pd.concat(est, axis=1).min(axis=1)
hi = pd.concat(est, axis=1).max(axis=1)
base = np.sqrt(lo * hi)                                              # geometric mean of the two anchor estimates
for k in obs:                                                        # anchors reproduce their observed values exactly
    lo[k] = hi[k] = base[k] = tpr[k]
d = d.set_index("metro")
d["tpr_low"], d["tpr_base"], d["tpr_high"] = lo, base, hi
for s in ("low", "base", "high"):
    d[f"trips_{s}"] = d[f"tpr_{s}"] * d.city_pop
d["est_from_chicago"], d["est_from_nyc"] = est["Chicago"], est["New York"]
d = d.reset_index()
d["anchor_year"] = YEAR
d.to_parquet(INTERIM / "demand.parquet", index=False)

x = d.set_index("metro")
cand = d[d.metro != "Las Vegas"]
vegas_rank_tpr = (cand.tpr_base > x.tpr_base["Las Vegas"]).sum() + 1
vegas_rank_pop = (cand.city_pop > x.city_pop["Las Vegas"]).sum() + 1
extra = "\n".join([
    f"Anchors (calendar {YEAR}): Chicago TNP trips {obs['Chicago']:,} / {a.city_pop['Chicago']:,.0f} residents = {tpr['Chicago']:.1f} per resident; "
    f"NYC HVFHV trips {obs['New York']:,} / {a.city_pop['New York']:,.0f} = {tpr['New York']:.1f} per resident.",
    f"Observed anchor ratio (NYC/Chicago trips per resident): {tpr['New York']/tpr['Chicago']:.2f}; demand-index ratio: {a.demand_index['New York']/a.demand_index['Chicago']:.2f}.",
    "The anchors do not rank the way the index does (Chicago has more trips per resident than NYC despite a lower index), which is why the spread between the two anchor-based estimates is wide.",
    f"Las Vegas base trips per resident {x.tpr_base['Las Vegas']:.1f} (rank {vegas_rank_tpr} of 26 including NYC and Chicago); city population rank {vegas_rank_pop} of 26.", "",
    "## Estimates (annual ride-hail trips per principal-city resident and total trips, millions)",
    d[["metro", "city_pop", "demand_index", "tpr_low", "tpr_base", "tpr_high", "trips_low", "trips_base", "trips_high"]].assign(
        city_pop=lambda z: z.city_pop.round(0), demand_index=lambda z: z.demand_index.round(3), tpr_low=lambda z: z.tpr_low.round(1),
        tpr_base=lambda z: z.tpr_base.round(1), tpr_high=lambda z: z.tpr_high.round(1), trips_low=lambda z: (z.trips_low / 1e6).round(1),
        trips_base=lambda z: (z.trips_base / 1e6).round(1), trips_high=lambda z: (z.trips_high / 1e6).round(1)).to_markdown(index=False)])
ok = write_profile("10_demand", d, [
    ("NYC estimate reproduces observed trips per resident", abs(x.tpr_base["New York"] - tpr["New York"]) < 1e-9 and abs(x.trips_base["New York"] - obs["New York"]) < 1),
    ("Chicago estimate reproduces observed trips per resident", abs(x.tpr_base["Chicago"] - tpr["Chicago"]) < 1e-9 and abs(x.trips_base["Chicago"] - obs["Chicago"]) < 1),
    ("low <= base <= high for every metro", bool(((d.tpr_low <= d.tpr_base + 1e-9) & (d.tpr_base <= d.tpr_high + 1e-9)).all())),
    ("Las Vegas trips per resident are in the top half of the 26 metros (high relative to its size)", vegas_rank_tpr <= 13),
    ("all estimates positive and finite", bool(np.isfinite(d[["tpr_low", "tpr_base", "tpr_high"]]).all().all() and (d.tpr_low > 0).all()))], extra=extra)
raise SystemExit(0 if ok else 1)
