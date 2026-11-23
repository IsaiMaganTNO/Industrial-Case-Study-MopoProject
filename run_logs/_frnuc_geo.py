import json, pandas as pd
from shapely.geometry import shape, Point
g=json.load(open(r"geodata\IC1_NWEU_FRLU.geojson",encoding="utf8"))
feats=[(f["properties"], shape(f["geometry"])) for f in g["features"]]
print("props keys:", list(feats[0][0].keys()))
fr=[(p,s) for p,s in feats if "FR" in json.dumps(p)]
for p,s in fr: print("FR feature:", p, "area(deg2)=", round(s.area,2), "bounds=", [round(b,2) for b in s.bounds])
df=pd.read_csv(r"data\Energy_Conversion\powerplants.csv", low_memory=False)
n=df[(df.Fueltype.str.contains("uclear",case=False,na=False))&(df.Country=="France")&(df.DateOut.isna())]
inside=0; out=[]
for _,r in n.iterrows():
    hit=[p for p,s in feats if s.contains(Point(r.lon,r.lat))]
    if any("FR" in json.dumps(p) for p in hit): inside+=r.Capacity
    else: out.append((r.Name, r.Capacity, [json.dumps(p)[:40] for p in hit]))
print("operating FR nuclear inside FR polygon:", inside, "MW")
print("outside:", round(sum(o[1] for o in out)), "MW")
for o in out[:60]: print("  ", o)
