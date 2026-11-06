"""Land config (metros.yaml, weights.yaml) as parquet so dbt reads every input from files."""
import pandas as pd, yaml
from common import *

cfg = yaml.safe_load(open(ROOT / "config/weights.yaml"))
load_metros()[["name", "state", "principal_city", "benchmark", "cbsa", "place_geoid"]].rename(columns={"name": "metro"}).to_parquet(INTERIM / "metros.parquet", index=False)
pd.DataFrame([dict(scenario=s, pillar=p, weight=w) for s, ws in cfg["scenarios"].items() for p, w in ws.items()]).to_parquet(INTERIM / "scenario_weights.parquet", index=False)
pd.DataFrame([dict(pillar=p, submetric=s, weight=v["weight"], direction=v["direction"]) for p, pv in cfg["pillars"].items()
              for s, v in pv["submetrics"].items()]).to_parquet(INTERIM / "submetric_weights.parquet", index=False)
pd.DataFrame([dict(status=k, weight=v) for k, v in cfg["crowding_status_weights"].items()]).to_parquet(INTERIM / "status_weights.parquet", index=False)
print("exported metros, scenario_weights, submetric_weights, status_weights")
