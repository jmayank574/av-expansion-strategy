"""Add city-center lat/lon (Open-Meteo geocoding API) to config/metros.yaml; keep Gazetteer point as gaz_lat/gaz_lon."""
import yaml, requests
STATE = {"NY":"New York","CA":"California","IL":"Illinois","TX":"Texas","DC":"Washington, D.C.","PA":"Pennsylvania","FL":"Florida",
 "GA":"Georgia","MA":"Massachusetts","AZ":"Arizona","MI":"Michigan","WA":"Washington","MN":"Minnesota","CO":"Colorado",
 "NC":"North Carolina","TN":"Tennessee","NV":"Nevada"}
cfg = yaml.safe_load(open("config/metros.yaml"))
for m in cfg["metros"]:
    res = requests.get("https://geocoding-api.open-meteo.com/v1/search",
        params=dict(name=m["principal_city"], count=50, language="en", format="json"), timeout=30).json().get("results", [])
    c = [x for x in res if x.get("country_code")=="US" and x.get("admin1") in (STATE[m["state"]], "District of Columbia")]
    c.sort(key=lambda x: -(x.get("population") or 0))
    assert c, (m["name"], [(x.get("admin1"),x.get("population")) for x in res])
    m.setdefault("gaz_lat", m["lat"]); m.setdefault("gaz_lon", m["lon"])
    m["lat"], m["lon"] = round(c[0]["latitude"],4), round(c[0]["longitude"],4)
    m["coord_source"] = f"Open-Meteo geocoding API, GeoNames id {c[0]['id']}"
    print(f'{m["name"]:18} {m["lat"]:8} {m["lon"]:9} gaz=({m["gaz_lat"]},{m["gaz_lon"]}) pop={c[0].get("population")}')
cfg["coordinate_note"] = "lat/lon = city-center point from Open-Meteo geocoding (GeoNames) as downtown proxy; gaz_lat/gaz_lon = Census Gazetteer internal point."
yaml.safe_dump(cfg, open("config/metros.yaml","w"), sort_keys=False)
