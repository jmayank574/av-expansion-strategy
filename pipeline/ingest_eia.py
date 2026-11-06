import pandas as pd, requests
from common import *

STATES = """AL Alabama|AK Alaska|AZ Arizona|AR Arkansas|CA California|CO Colorado|CT Connecticut|DE Delaware|DC District of Columbia|FL Florida|GA Georgia|HI Hawaii|ID Idaho|IL Illinois|IN Indiana|IA Iowa|KS Kansas|KY Kentucky|LA Louisiana|ME Maine|MD Maryland|MA Massachusetts|MI Michigan|MN Minnesota|MS Mississippi|MO Missouri|MT Montana|NE Nebraska|NV Nevada|NH New Hampshire|NJ New Jersey|NM New Mexico|NY New York|NC North Carolina|ND North Dakota|OH Ohio|OK Oklahoma|OR Oregon|PA Pennsylvania|RI Rhode Island|SC South Carolina|SD South Dakota|TN Tennessee|TX Texas|UT Utah|VT Vermont|VA Virginia|WA Washington|WV West Virginia|WI Wisconsin|WY Wyoming"""
ABBR = {x[3:]: x[:2] for x in STATES.split("|")}

F = RAW / "eia_5_6_b.xlsx"
if not F.exists():
    F.write_bytes(requests.get("https://www.eia.gov/electricity/monthly/xls/table_5_06_b.xlsx", timeout=60).content)
e = pd.read_excel(F, header=None)
title, period = e.iloc[1, 0], e.iloc[3, 3]
assert e.iloc[2, 3] == "Commercial", e.iloc[2, 3]
df = pd.DataFrame({"state_name": e.iloc[4:, 0].astype(str).str.strip(),
                   "commercial_cents_kwh": pd.to_numeric(e.iloc[4:, 3], errors="coerce")}).dropna()
df["state"] = df.state_name.map(ABBR)
df = df.dropna(subset=["state"]).reset_index(drop=True)
df["eia_period"] = period
df.to_parquet(INTERIM / "eia.parquet", index=False)
ok = write_profile("06_eia", df, [
    ("all states of the 26 metros present", set(load_metros().state) <= set(df.state)),
    ("values for the study states in 8-30 c/kWh", bool(df[df.state.isin(set(load_metros().state))].commercial_cents_kwh.between(8, 30).all()))],
    extra=f"Outside 8-30 nationally (not used by any metro): "+", ".join(f"{r.state} {r.commercial_cents_kwh}" for r in df[~df.commercial_cents_kwh.between(8,30)].itertuples())+f". Table 5.6.B, commercial sector, {period}: a year-to-date average, not a 12-month average (chosen by user). {title}")
raise SystemExit(0 if ok else 1)
