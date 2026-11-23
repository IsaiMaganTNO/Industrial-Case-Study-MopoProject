import json
d=json.load(open(r".spinetoolbox/project.json",encoding="utf-8"))
items=d["items"]
for k,v in items.items():
    if v.get("specification")=="ines_builder":
        print(k, json.dumps(v, indent=1)[:900])
