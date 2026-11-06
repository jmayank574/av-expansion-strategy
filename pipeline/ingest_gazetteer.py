import pandas as pd
from common import *

m = load_metros()
g = pd.read_csv(RAW / "census/2025_Gaz_place_national.txt", sep="|", dtype={"GEOID": str}, encoding="latin-1")
g.columns = [c.strip() for c in g.columns]
df = m[["name", "place_geoid"]].rename(columns={"name": "metro"}).merge(
    g[["GEOID", "ALAND_SQMI"]], left_on="place_geoid", right_on="GEOID", how="left")
acs = pd.read_parquet(INTERIM / "acs.parquet")[["metro", "city_pop"]]
df = df.merge(acs, on="metro").rename(columns={"ALAND_SQMI": "land_sqmi"}).drop(columns="GEOID")
df["density_per_sqmi"] = df.city_pop / df.land_sqmi
df.to_parquet(INTERIM / "gazetteer.parquet", index=False)
top = df.sort_values("density_per_sqmi", ascending=False).metro.head(5).tolist()
ok = write_profile("02_gazetteer", df, [
    ("all 26 present, no null area", len(df) == 26 and bool(df.land_sqmi.notna().all())),
    ("NYC has highest density", top[0] == "New York"),
    ("SF, Boston or Chicago in positions 2-4", len({"San Francisco", "Boston", "Chicago"} & set(top[1:4])) >= 1)],
    extra="Top 5 density: " + ", ".join(top))
raise SystemExit(0 if ok else 1)
