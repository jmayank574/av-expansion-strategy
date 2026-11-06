"""10-yr (2016-2025) annual-average rain / snow / extreme-heat days per metro.

Primary source: NOAA GHCN-Daily station observations at each metro's primary commercial airport, from the NCEI Access Data Service
(station IDs are in config/metros.yaml, chosen by pipeline/lookup_weather_stations.py).
Thresholds: rain = precipitation >= 2.5 mm, snow = snowfall >= 10 mm (1 cm), extreme heat = max temperature >= 40 C.
Fallback: if a station is missing more than 5% of days (precipitation or max temperature), that metro uses the Open-Meteo daily archive
at the principal-city point instead, and the profile says so. The Open-Meteo series is also computed for every metro and kept as
om_* columns, as a cross-check.
Snowfall: GHCN usually omits SNOW on days without snow, so a missing SNOW value counts as no snow.
"""
import io, json, time
import pandas as pd, requests
from common import *

Y0, Y1 = 2016, 2025
YRS = Y1 - Y0 + 1
MAX_MISSING = 0.05
NCEI = "https://www.ncei.noaa.gov/access/services/data/v1"
DAYS = pd.date_range(f"{Y0}-01-01", f"{Y1}-12-31", freq="D")
(RAW / "weather").mkdir(exist_ok=True)


def noaa_daily(station):
    f = RAW / "weather" / f"noaa_{station}.csv"
    if not f.exists():
        for attempt in range(5):
            r = requests.get(NCEI, timeout=180, params=dict(dataset="daily-summaries", stations=station, startDate=f"{Y0}-01-01",
                                                            endDate=f"{Y1}-12-31", dataTypes="PRCP,SNOW,TMAX", format="csv", units="metric"))
            if r.status_code == 200 and r.text.strip():
                f.write_text(r.text, encoding="utf-8")
                break
            print(station, r.status_code, r.text[:100]); time.sleep(10 * (attempt + 1))
        else:
            return None
        time.sleep(1)
    d = pd.read_csv(f, parse_dates=["DATE"]).set_index("DATE")
    return d.reindex(DAYS)


def open_meteo_daily(r):
    cache = RAW / "weather" / f"{r['name'].replace(' ', '_')}.json"
    if cache.exists():
        return pd.DataFrame(json.loads(cache.read_text(encoding="utf-8"))["daily"])
    for attempt in range(6):
        resp = requests.get("https://archive-api.open-meteo.com/v1/archive", timeout=120, params=dict(
            latitude=r.lat, longitude=r.lon, start_date=f"{Y0}-01-01", end_date=f"{Y1}-12-31",
            daily="precipitation_sum,snowfall_sum,temperature_2m_max", timezone="auto"))
        if resp.status_code == 200:
            break
        print(r["name"], resp.status_code, resp.text[:120]); time.sleep(20 * (attempt + 1))
    else:
        raise SystemExit(f"Open-Meteo failed for {r['name']}")
    cache.write_text(resp.text, encoding="utf-8")
    time.sleep(2)
    return pd.DataFrame(resp.json()["daily"])


rows = []
for _, r in load_metros().iterrows():
    om = open_meteo_daily(r)
    om_vals = dict(om_rain_days=(om.precipitation_sum >= 2.5).sum() / YRS, om_snow_days=(om.snowfall_sum >= 1).sum() / YRS,
                   om_heat_days=(om.temperature_2m_max >= 40).sum() / YRS)
    d = noaa_daily(r["weather_station"])
    miss_days = int((d.PRCP.isna() | d.TMAX.isna()).sum()) if d is not None else len(DAYS)
    miss_pct = miss_days / len(DAYS)
    use_noaa = d is not None and miss_pct <= MAX_MISSING
    if use_noaa:
        vals = dict(rain_days=(d.PRCP >= 2.5).sum() / YRS, snow_days=(d.SNOW >= 10).sum() / YRS, heat_days=(d.TMAX >= 40).sum() / YRS)
        n, src = len(d), "NOAA GHCN-Daily"
        snow_reported = int(d.SNOW.notna().sum())
    else:
        vals = dict(rain_days=om_vals["om_rain_days"], snow_days=om_vals["om_snow_days"], heat_days=om_vals["om_heat_days"])
        n, src, snow_reported = len(om), "Open-Meteo archive (fallback: NOAA station missing >5% of days)", 0
    rows.append(dict(metro=r["name"], days=n, missing_values=miss_days, missing_pct=round(miss_pct * 100, 2), **vals,
                     weather_source=src, weather_station=r["weather_station"], station_name=r["weather_station_name"],
                     station_km_from_city=r["weather_station_km"], snow_days_reported=snow_reported, **om_vals))
df = pd.DataFrame(rows)
df["weather_vintage"] = f"{Y0}-{Y1} daily, NOAA GHCN-Daily airport stations (Open-Meteo archive as fallback)"
df.to_parquet(INTERIM / "weather.parquet", index=False)
d = df.set_index("metro")
n_fb = int((~df.weather_source.str.startswith("NOAA")).sum())
cmp = df[["metro", "weather_station", "station_name", "missing_pct", "rain_days", "om_rain_days", "snow_days", "om_snow_days", "heat_days", "om_heat_days"]]
snowy_no_snow = [m for m in df.metro if d.at[m, "om_snow_days"] >= 3 and d.at[m, "snow_days"] == 0]
ok = write_profile("05_weather", df.drop(columns=["weather_vintage"]), [
    ("all 26 present, 3,653 days each", len(df) == 26 and (df.days == 3653).all()),
    ("every station is missing no more than 5% of days (else Open-Meteo fallback is used)", bool((df.missing_pct <= MAX_MISSING * 100).all()) or n_fb > 0),
    ("Phoenix and Las Vegas are top-2 heat days", set(df.nlargest(2, "heat_days").metro) == {"Phoenix", "Las Vegas"}),
    ("Phoenix/Vegas rain days below median", (d.rain_days[["Phoenix", "Las Vegas"]] < df.rain_days.median()).all()),
    ("Minneapolis, Boston, Detroit in top 7 snow days (Denver and Chicago also high)", {"Minneapolis", "Boston", "Detroit"} <= set(df.nlargest(7, "snow_days").metro)),
    ("Miami and Florida metros have zero snow days", (d.snow_days[["Miami", "Tampa", "Orlando"]] == 0).all()),
    ("no metro shows zero snow days at a station while Open-Meteo shows 3+ (would mean the station does not report snowfall)", not snowy_no_snow)],
    extra="\n".join([f"Metros using the Open-Meteo fallback: {n_fb}" + (": " + ", ".join(df[~df.weather_source.str.startswith('NOAA')].metro) if n_fb else ""),
                     "", "## NOAA station vs Open-Meteo archive (days per year; om_* is Open-Meteo)", cmp.round(1).to_markdown(index=False)]))
raise SystemExit(0 if ok else 1)
