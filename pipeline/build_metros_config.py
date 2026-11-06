"""Generate config/metros.yaml. CBSA codes come from the Census delineation file; place FIPS
and downtown-proxy coordinates from the Census Gazetteer. Only names/airports are typed here."""
import pandas as pd, yaml, pathlib
RAW = pathlib.Path("data/raw/census")
# display, CBSA-title prefix, principal city, state, Gazetteer name, airports
SPEC = [
 ("New York","New York-Newark","New York","NY","New York city",["JFK","LGA","EWR"]),
 ("Los Angeles","Los Angeles-Long Beach","Los Angeles","CA","Los Angeles city",["LAX","BUR","LGB","SNA"]),
 ("Chicago","Chicago-Naperville","Chicago","IL","Chicago city",["ORD","MDW"]),
 ("Dallas-Fort Worth","Dallas-Fort Worth","Dallas","TX","Dallas city",["DFW","DAL"]),
 ("Houston","Houston-","Houston","TX","Houston city",["IAH","HOU"]),
 ("Washington DC","Washington-Arlington","Washington","DC","Washington city",["DCA","IAD"]),
 ("Philadelphia","Philadelphia-Camden","Philadelphia","PA","Philadelphia city",["PHL"]),
 ("Miami","Miami-Fort Lauderdale","Miami","FL","Miami city",["MIA","FLL","PBI"]),
 ("Atlanta","Atlanta-Sandy","Atlanta","GA","Atlanta city",["ATL"]),
 ("Boston","Boston-Cambridge","Boston","MA","Boston city",["BOS"]),
 ("Phoenix","Phoenix-Mesa","Phoenix","AZ","Phoenix city",["PHX"]),
 ("San Francisco","San Francisco-Oakland","San Francisco","CA","San Francisco city",["SFO","OAK"]),
 ("Detroit","Detroit-Warren","Detroit","MI","Detroit city",["DTW"]),
 ("Seattle","Seattle-Tacoma","Seattle","WA","Seattle city",["SEA"]),
 ("Minneapolis","Minneapolis-St. Paul","Minneapolis","MN","Minneapolis city",["MSP"]),
 ("San Diego","San Diego-Chula","San Diego","CA","San Diego city",["SAN"]),
 ("Tampa","Tampa-St. Petersburg","Tampa","FL","Tampa city",["TPA"]),
 ("Denver","Denver-Aurora","Denver","CO","Denver city",["DEN"]),
 ("Orlando","Orlando-Kissimmee","Orlando","FL","Orlando city",["MCO"]),
 ("Charlotte","Charlotte-Concord","Charlotte","NC","Charlotte city",["CLT"]),
 ("San Antonio","San Antonio-New Braunfels","San Antonio","TX","San Antonio city",["SAT"]),
 ("Austin","Austin-Round Rock","Austin","TX","Austin city",["AUS"]),
 ("Nashville","Nashville-Davidson","Nashville","TN","Nashville-Davidson metropolitan government (balance)",["BNA"]),
 ("Pittsburgh","Pittsburgh,","Pittsburgh","PA","Pittsburgh city",["PIT"]),
 ("Sacramento","Sacramento-Roseville","Sacramento","CA","Sacramento city",["SMF"]),
 ("Las Vegas","Las Vegas-Henderson","Las Vegas","NV","Las Vegas city",["LAS"]),
]
d = pd.read_excel(RAW/"list1_2023.xlsx", header=2, dtype=str)
d = d[d["Metropolitan/Micropolitan Statistical Area"]=="Metropolitan Statistical Area"]
cb = d[["CBSA Code","CBSA Title"]].drop_duplicates()
g = pd.read_csv(RAW/"2025_Gaz_place_national.txt", sep="|", dtype={"GEOID":str}, encoding="latin-1")
g.columns = [c.strip() for c in g.columns]
out = []
for disp, pref, city, st, gname, aps in SPEC:
    m = cb[cb["CBSA Title"].str.startswith(pref)]
    assert len(m)==1, (disp, m)
    p = g[(g.USPS==st)&(g.NAME==gname)]
    assert len(p)==1, (disp, p)
    p = p.iloc[0]
    out.append(dict(name=disp, benchmark=(disp=="Las Vegas"), cbsa=m.iloc[0,0], cbsa_title=m.iloc[0,1],
        principal_city=city, state=st, state_fips=p.GEOID[:2], place_fips=p.GEOID[2:], place_geoid=p.GEOID,
        census_place_name=gname, lat=round(float(p.INTPTLAT),4), lon=round(float(p.INTPTLONG),4),
        land_sqmi=float(p.ALAND_SQMI), airports=aps))
yaml.safe_dump({"metros": out, "coordinate_note": "lat/lon are Census Gazetteer internal points of the principal city (a proxy for downtown)."},
    open("config/metros.yaml","w"), sort_keys=False)
print(pd.DataFrame(out)[["name","cbsa","state","place_geoid","lat","lon","land_sqmi"]].to_string())
