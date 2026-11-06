"""10-yr (2016-2025) annual-average rain/snow/extreme-heat days per metro from Open-Meteo daily archive."""
import pandas as pd, requests, time, json
from common import *

Y0, Y1 = 2016, 2025
rows = []
for _, r in load_metros().iterrows():
    cache = RAW / "weather" / f"{r['name'].replace(' ', '_')}.json"
    cache.parent.mkdir(exist_ok=True)
    if cache.exists():
        daily = pd.DataFrame(json.loads(cache.read_text(encoding="utf-8"))["daily"])
    else:
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
        daily = pd.DataFrame(resp.json()["daily"])
        time.sleep(2)
    n = len(daily)
    miss = int(daily[["precipitation_sum", "snowfall_sum", "temperature_2m_max"]].isna().sum().sum())
    yrs = Y1 - Y0 + 1
    rows.append(dict(metro=r["name"], days=n, missing_values=miss,
                     rain_days=(daily.precipitation_sum >= 2.5).sum() / yrs,
                     snow_days=(daily.snowfall_sum >= 1).sum() / yrs,
                     heat_days=(daily.temperature_2m_max >= 40).sum() / yrs))
df = pd.DataFrame(rows)
df["weather_vintage"] = f"{Y0}-{Y1} daily, Open-Meteo archive"
df.to_parquet(INTERIM / "weather.parquet", index=False)
d = df.set_index("metro")
ok = write_profile("05_weather", df, [
    ("all 26 present with 3,653 days and no missing values", len(df) == 26 and (df.days == 3653).all() and df.missing_values.sum() == 0),
    ("Phoenix and Las Vegas are top-2 heat days", set(df.nlargest(2, "heat_days").metro) == {"Phoenix", "Las Vegas"}),
    ("Phoenix/Vegas rain days below median", (d.rain_days[["Phoenix", "Las Vegas"]] < df.rain_days.median()).all()),
    ("Minneapolis, Boston, Detroit in top 7 snow days (Denver and Chicago also high)", {"Minneapolis", "Boston", "Detroit"} <= set(df.nlargest(7, "snow_days").metro)),
    ("Miami and Florida metros have zero snow days", (d.snow_days[["Miami", "Tampa", "Orlando"]] == 0).all())])
raise SystemExit(0 if ok else 1)
