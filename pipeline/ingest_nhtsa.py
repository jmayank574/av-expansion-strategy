"""NHTSA SGO ADS incidents: latest version per Report ID, one row per Same Incident ID, last 24 months,
mapped to metros by city/state (fallback: Census Gazetteer city point within 40 km of the principal city center)."""
import pandas as pd, numpy as np, re, requests
from common import *

URLS = {"ads_current.csv": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv",
        "ads_archive.csv": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADS.csv"}
COLS = ["Report ID", "Report Version", "Reporting Entity", "Operating Entity", "Same Incident ID", "Incident Date",
        "Latitude", "Longitude", "City", "State"]
frames = []
for fn, url in URLS.items():
    f = RAW / "nhtsa" / fn
    f.parent.mkdir(exist_ok=True)
    if not f.exists():
        f.write_bytes(requests.get(url, timeout=120).content)
    d = pd.read_csv(f, low_memory=False, encoding="latin-1", usecols=lambda c: c in COLS)
    d["source_file"] = fn
    frames.append(d)
raw = pd.concat(frames, ignore_index=True)
n_raw = len(raw)

raw["Report Version"] = pd.to_numeric(raw["Report Version"])
latest = raw.sort_values("Report Version").groupby("Report ID", as_index=False).tail(1)
latest = latest.assign(incident_month=pd.to_datetime(latest["Incident Date"], format="%b-%Y", errors="coerce"))
latest = latest.dropna(subset=["incident_month"])
end = latest.incident_month.max()
start = end - pd.DateOffset(months=23)                       # 24 calendar months ending at latest incident month
win = latest[latest.incident_month >= start]
inc = win.sort_values(["Report Version", "incident_month"]).groupby("Same Incident ID", as_index=False).tail(1)

def clean_entity(s):
    s = re.sub(r"[,\.]", "", str(s)).strip()
    s = re.sub(r"\s+(LLC|Inc|Corp|Corporation)$", "", s, flags=re.I)
    return s
inc = inc.assign(operating_entity=inc["Operating Entity"].fillna(inc["Reporting Entity"]).map(clean_entity))

m = load_metros()
city_key = {(r.principal_city.lower(), r.state): r["name"] for _, r in m.iterrows()}
# neighborhoods / in-CBSA cities that the 40 km Gazetteer rule misses
city_key.update({("venice", "CA"): "Los Angeles", ("fort worth", "TX"): "Dallas-Fort Worth", ("kingwood", "TX"): "Houston"})
inc = inc.assign(metro=[city_key.get((str(c).strip().lower(), str(s).strip().upper())) for c, s in zip(inc.City, inc.State)])

def hav(lat1, lon1, lat2, lon2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * np.arcsin(np.sqrt(a))

# fallback for suburbs: Census Gazetteer internal point of the reported city/state, nearest metro center within 40 km
n_city = int(inc.metro.notna().sum())
inc["City"] = inc.City.fillna("").astype(str).str.strip(); inc["State"] = inc.State.fillna("").astype(str).str.strip().str.upper()
gz = pd.read_csv(RAW / "census/2025_Gaz_place_national.txt", sep="|", encoding="latin-1")
gz.columns = [c.strip() for c in gz.columns]
gz["key"] = gz.NAME.str.replace(r"\s+(city|town|village|CDP|borough|municipality|city and borough)$", "", regex=True).str.lower()
gz = gz.sort_values("ALAND_SQMI", ascending=False).drop_duplicates(["USPS", "key"]).set_index(["USPS", "key"])
via_coord = 0
for i in inc.index[inc.metro.isna()]:
    k = (inc.at[i, "State"], inc.at[i, "City"].lower())
    if k in gz.index:
        dist = hav(gz.at[k, "INTPTLAT"], gz.at[k, "INTPTLONG"], m.lat.values, m.lon.values)
        j = dist.argmin()
        if dist[j] <= 40:
            inc.at[i, "metro"] = m["name"].iloc[j]; via_coord += 1
miss = inc.metro.isna()

inc["months_window"] = f"{start:%Y-%m} to {end:%Y-%m}"
out = inc[["Report ID", "Same Incident ID", "operating_entity", "incident_month", "City", "State", "metro", "source_file"]].rename(
    columns={"Report ID": "report_id", "Same Incident ID": "same_incident_id", "City": "city", "State": "state"})
out.to_parquet(INTERIM / "nhtsa_incidents.parquet", index=False)
counts = out.dropna(subset=["metro"]).groupby(["metro", "operating_entity"]).size().rename("ads_incidents").reset_index()
counts.to_parquet(INTERIM / "nhtsa.parquet", index=False)

unm = out[out.metro.isna()].groupby(["city", "state"]).size().sort_values(ascending=False)
extra = "\n".join([
    f"Raw rows {n_raw} (current + archive) -> latest version per Report ID {len(latest)} -> window {start:%Y-%m}..{end:%Y-%m} -> one per Same Incident ID {len(inc)}.",
    f"Mapped by city/state: {n_city}; mapped by Gazetteer city point (<=40 km of downtown): {via_coord}; unmapped: {int(out.metro.isna().sum())}.",
    "", "## Top operating entities", out.operating_entity.value_counts().head(10).to_frame().to_markdown(),
    "", "## Top cities", out.groupby(["city", "state"]).size().sort_values(ascending=False).head(12).to_frame("n").to_markdown(),
    "", "## Incidents by metro (candidates + benchmark)", out.metro.value_counts().to_frame("n").to_markdown(),
    "", "## Unmapped cities (top 25)", unm.head(25).to_frame("n").to_markdown(),
    "", "NHTSA SGO reports carry no mileage: counts show where operators are active, not safety rates."])
ok = write_profile("04_nhtsa", counts, [
    ("no duplicate Same Incident ID", out.same_incident_id.is_unique),
    ("no duplicate Report ID", out.report_id.is_unique),
    ("window is 24 months", len(pd.period_range(start, end, freq="M")) == 24),
    ("Waymo is the top operating entity", out.operating_entity.value_counts().index[0] == "Waymo"),
    ("majority of incidents mapped to a metro", out.metro.notna().mean() > 0.5)], extra=extra)
raise SystemExit(0 if ok else 1)
