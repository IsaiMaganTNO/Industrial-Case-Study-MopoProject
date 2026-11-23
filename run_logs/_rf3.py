import json
p=r".spinetoolbox\project.json"
d=json.load(open(p,encoding="utf-8"))
import re
s=json.dumps(d)
for k,v in d["items"].items():
    if "biomass" in k:
        print("=== ",k); print(json.dumps(v,indent=1)[:1800])
