import json
p=r".spinetoolbox\project.json"
s=open(p,encoding="utf-8").read()
old="data/Biomass/db_biomass_ener_mopo.csv"
new="data/Biomass/db_biomass_ener_mopo_mixedres.csv"
print("occurrences:",s.count(old))
s=s.replace(old,new)
open(p,"w",encoding="utf-8").write(s)
d=json.load(open(p,encoding="utf-8"))
print("valid json, items:",len(d["items"]))
print("check:",s.count(new))
