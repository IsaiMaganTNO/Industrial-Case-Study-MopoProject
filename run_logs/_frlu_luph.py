import json, sqlite3
from shapely.geometry import shape, Point
import pandas as pd
g = json.load(open(r"geodata\IC1_NWEU_FRLU.geojson", encoding="utf8"))
lu = [shape(f["geometry"]) for f in g["features"] if f["properties"]["id"]=="LU"][0]
pp = pd.read_csv(r"data\Energy_Conversion\powerplants.csv", low_memory=False)
x = pp[pp.Country=="Luxembourg"]
print(x[["Name","Technology","Capacity","lat","lon"]].sort_values("Capacity", ascending=False).head(5).to_string())
for _, r in x.sort_values("Capacity", ascending=False).head(3).iterrows():
    print(r["Name"], lu.contains(Point(r["lon"], r["lat"])))
d = sqlite3.connect(r".spinetoolbox\items\power_db\power_db.sqlite")
print("power_db LU entities:", [n for (n,) in d.execute("select name from entity where name like '%LU'")][:20])
