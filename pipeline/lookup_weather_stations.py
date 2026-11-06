"""Pick one NOAA GHCN-Daily station per metro from NOAA's own station inventory and record it in config/metros.yaml.

Rule: the station (ID starting USW: first-order / ASOS-type, with PRCP and TMAX records covering 2016-2025 in ghcnd-inventory.txt)
nearest to the metro's primary commercial airport, using airport coordinates from the OurAirports public dataset (keyed by IATA code),
and requiring it to be within 8 km of that airport. If the primary airport has no such station the next airport in metros.yaml is tried;
failing that, the nearest qualifying station to the principal-city point is used and flagged in the output.
Run once (or after changing the metro list): python pipeline/lookup_weather_stations.py
"""
import math, requests, yaml
import pandas as pd
from common import *

BASE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
CACHE = RAW / "weather"
CACHE.mkdir(exist_ok=True)
Y0, Y1 = 2016, 2025


def fetch(name):
    f = CACHE / name
    if not f.exists():
        r = requests.get(BASE + name, timeout=300)
        r.raise_for_status()
        f.write_bytes(r.content)
    return f.read_text(encoding="latin-1").splitlines()


def hav(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


stations = {}
for ln in fetch("ghcnd-stations.txt"):
    if ln.startswith("USW"):
        stations[ln[0:11]] = (float(ln[12:20]), float(ln[21:30]), ln[38:40].strip(), ln[41:71].strip())
cover = {}
for ln in fetch("ghcnd-inventory.txt"):
    sid, el = ln[0:11], ln[31:35]
    if sid in stations and el in ("PRCP", "TMAX"):
        cover.setdefault(sid, {})[el] = (int(ln[36:40]), int(ln[41:45]))
ok = {s: v for s, v in stations.items() if len(cover.get(s, {})) == 2 and all(a <= Y0 and b >= Y1 for a, b in cover[s].values())}
print(f"{len(stations)} USW stations, {len(ok)} with PRCP+TMAX covering {Y0}-{Y1}")

oa = CACHE / "ourairports_airports.csv"
if not oa.exists():
    oa.write_bytes(requests.get("https://davidmegginson.github.io/ourairports-data/airports.csv", timeout=120).content)
ap = pd.read_csv(oa, dtype=str).dropna(subset=["iata_code"]).drop_duplicates("iata_code").set_index("iata_code")

path = ROOT / "config/metros.yaml"
cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
rows = []
for m in cfg["metros"]:
    pick, how = None, ""
    for iata in m["airports"]:
        if iata not in ap.index:
            continue
        alat, alon = float(ap.at[iata, "latitude_deg"]), float(ap.at[iata, "longitude_deg"])
        d, sid = min((hav(alat, alon, v[0], v[1]), s) for s, v in ok.items())
        if d <= 8:
            pick, how = sid, f"at {iata} airport ({d:.1f} km from it)"
            break
    if pick is None:
        _, pick = min((hav(m["lat"], m["lon"], v[0], v[1]), s) for s, v in ok.items())
        how = "NO airport match: nearest to city point"
    la, lo, st, nm = stations[pick]
    km = hav(m["lat"], m["lon"], la, lo)
    m["weather_station"], m["weather_station_name"], m["weather_station_km"] = pick, nm, round(km, 1)
    rows.append((m["name"], pick, nm, st, km, how))
cfg["weather_station_note"] = ("weather_station = NOAA GHCN-Daily station (USW*) at the primary commercial airport, with PRCP and TMAX covering "
                               "2016-2025, chosen by pipeline/lookup_weather_stations.py from NOAA's ghcnd-stations.txt and ghcnd-inventory.txt")
path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
for r in rows:
    print(f"{r[0]:18s} {r[1]} {r[2]:34s} {r[3]} {r[4]:5.1f} km from city | {r[5]}")
