import requests, pandas as pd, json
from common import *

VINTAGE = 2024
BASE = f"https://api.census.gov/data/{VINTAGE}/acs/acs5"
KEY = env("CENSUS_API_KEY")
VARS = {"B01003_001E": "pop", "B08201_001E": "households", "B08201_002E": "hh_no_vehicle",
        "B08301_001E": "workers_16plus", "B08301_016E": "taxi_ridehail_commuters", "B19013_001E": "median_hh_income"}

# confirm each variable against the vintage's variables.json before use
vj = json.load(open(RAW / "census/variables_2024.json"))["variables"]
for v in VARS:
    assert v in vj, v
assert "Taxi or ride-hailing" in vj["B08301_016E"]["label"] and "No vehicle" in vj["B08201_002E"]["label"]


def get(params):
    r = requests.get(BASE, params={**params, "key": KEY}, timeout=60)
    r.raise_for_status()
    j = r.json()
    return pd.DataFrame(j[1:], columns=j[0])


get_vars = "NAME," + ",".join(VARS)
metro = get({"get": get_vars, "for": "metropolitan statistical area/micropolitan statistical area:*"})
metro = metro.rename(columns={"metropolitan statistical area/micropolitan statistical area": "cbsa"})
m = load_metros()
places = pd.concat([get({"get": get_vars, "for": "place:*", "in": f"state:{s}"}) for s in sorted(m.state_fips.unique())])
places["place_geoid"] = places.state + places.place
(RAW / "census").mkdir(exist_ok=True)
metro.to_csv(RAW / "census/acs_metro_raw.csv", index=False)
places.to_csv(RAW / "census/acs_places_raw.csv", index=False)


def num(x):
    # Census encodes nulls as large negative sentinels
    x = float(x) if x not in (None, "") else float("nan")
    return x if x >= 0 else float("nan")


rows = []
for _, r in m.iterrows():
    a = metro[metro.cbsa == r.cbsa]
    p = places[places.place_geoid == r.place_geoid]
    assert len(a) == 1 and len(p) == 1, r["name"]
    a, p = a.iloc[0], p.iloc[0]
    rows.append(dict(metro=r["name"], cbsa=r.cbsa, place_geoid=r.place_geoid, metro_pop=num(a.B01003_001E),
                     city_pop=num(p.B01003_001E), city_households=num(p.B08201_001E),
                     city_hh_no_vehicle=num(p.B08201_002E), city_workers=num(p.B08301_001E),
                     city_taxi_ridehail=num(p.B08301_016E), city_median_hh_income=num(p.B19013_001E)))
df = pd.DataFrame(rows)
df["no_vehicle_share"] = df.city_hh_no_vehicle / df.city_households
df["taxi_ridehail_share"] = df.city_taxi_ridehail / df.city_workers
df["acs_vintage"] = f"{VINTAGE} 5-year (2020-2024)"
df.to_parquet(INTERIM / "acs.parquet", index=False)
d = df.set_index("metro")
ok = write_profile("01_acs", df, [
    ("all 26 metros present", len(df) == 26 and df.metro.nunique() == 26),
    ("NYC metro pop roughly 19-20M", 19e6 <= d.metro_pop["New York"] <= 20e6),
    ("shares between 0 and 1", bool(df[["no_vehicle_share", "taxi_ridehail_share"]].stack().between(0, 1).all())),
    ("no nulls in numeric fields", int(df.select_dtypes("number").isna().sum().sum()) == 0),
    ("NYC no-vehicle share > 0.4", d.no_vehicle_share["New York"] > 0.4)],
    extra="Source: ACS 5-year 2024 API. Variables: " + json.dumps(VARS))
raise SystemExit(0 if ok else 1)
