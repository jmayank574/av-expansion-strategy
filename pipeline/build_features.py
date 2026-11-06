"""Join interim sources into one raw feature table (26 rows) -> data/interim/features.parquet."""
import numpy as np, pandas as pd, yaml
from common import *

m = load_metros()[["name", "state", "principal_city", "benchmark"]].rename(columns={"name": "metro"})
acs = pd.read_parquet(INTERIM / "acs.parquet")
gz = pd.read_parquet(INTERIM / "gazetteer.parquet")[["metro", "land_sqmi", "density_per_sqmi"]]
faa = pd.read_parquet(INTERIM / "faa.parquet")[["metro", "enplanements", "enplanements_per_resident"]]
wx = pd.read_parquet(INTERIM / "weather.parquet")[["metro", "rain_days", "snow_days", "heat_days"]]
eia = pd.read_parquet(INTERIM / "eia.parquet")[["state", "commercial_cents_kwh"]]
reg = pd.read_parquet(INTERIM / "regulation.parquet")[["state", "tier", "new_entrant_path"]]
PATH_SCORE = {"slow": 0, "moderate": 1, "fast": 2}   # ordinal; percentile ranking only uses the order
reg["new_entrant_score"] = reg.new_entrant_path.map(PATH_SCORE)
comp = pd.read_parquet(INTERIM / "competitors.parquet")
W = yaml.safe_load(open(ROOT / "config/weights.yaml"))["crowding_status_weights"]
comp = comp[comp.is_operator != "true"].copy()      # the operator's own presence is not competition
comp["w"] = comp.status.map(W)
crowd = comp.groupby("metro").agg(crowding=("w", "sum"), n_competitors=("competitor", "nunique")).reset_index()

f = (m.merge(acs.drop(columns=["cbsa", "place_geoid"]), on="metro").merge(gz, on="metro").merge(faa, on="metro").merge(wx, on="metro")
       .merge(eia, on="state").merge(reg, on="state").merge(crowd, on="metro", how="left"))
f[["crowding", "n_competitors"]] = f[["crowding", "n_competitors"]].fillna(0)
f["crowding"] = f.crowding.round(6)    # float sums differ by summation order (dbt vs pandas); rounding keeps true ties tied
f = f.rename(columns={"density_per_sqmi": "city_density", "tier": "reg_tier", "commercial_cents_kwh": "elec_cents_kwh"})
f["log_metro_pop"] = np.log(f.metro_pop)
assert len(f) == 26 and f.isna().sum().sum() == 0, f.isna().sum()
f.to_parquet(INTERIM / "features.parquet", index=False)
ok = write_profile("08_features", f.drop(columns=["acs_vintage"]), [
    ("26 rows, no nulls", len(f) == 26 and f.isna().sum().sum() == 0),
    ("exactly one benchmark (Las Vegas)", f.benchmark.sum() == 1 and f[f.benchmark].metro.iloc[0] == "Las Vegas"),
    ("crowding >= 0", bool((f.crowding >= 0).all()))])
raise SystemExit(0 if ok else 1)
