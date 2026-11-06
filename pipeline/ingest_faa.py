import pandas as pd, warnings, requests
from common import *

warnings.filterwarnings("ignore")
F = RAW / "faa_cy2025.xlsx"
if not F.exists():
    F.write_bytes(requests.get("https://www.faa.gov/airports/planning_capacity/passenger_allcargo_stats/passenger/"
                               "arp-cy2025-commercial-service-enplanements.xlsx", timeout=60).content)
f = pd.read_excel(F).set_index("Locid")
rows = []
for _, r in load_metros().iterrows():
    miss = [a for a in r.airports if a not in f.index]
    assert not miss, (r["name"], miss)
    rows.append(dict(metro=r["name"], airports=",".join(r.airports),
                     enplanements=float(sum(f.loc[a, "CY 25 Enplanements"] for a in r.airports))))
df = pd.DataFrame(rows).merge(pd.read_parquet(INTERIM / "acs.parquet")[["metro", "metro_pop"]], on="metro")
df["enplanements_per_resident"] = df.enplanements / df.metro_pop
df["faa_vintage"] = "CY2025"
df.to_parquet(INTERIM / "faa.parquet", index=False)
d = df.set_index("metro")
ok = write_profile("03_faa", df, [
    ("all 26 present", len(df) == 26),
    ("Atlanta among top 3 by enplanements", "Atlanta" in df.nlargest(3, "enplanements").metro.tolist()),
    ("Vegas per-resident rank is 1 or 2 of 26", d.enplanements_per_resident.rank(ascending=False)["Las Vegas"] <= 2)],
    extra="Miami uses DJT (FAA Locid for West Palm Beach, IATA PBI).")
raise SystemExit(0 if ok else 1)
