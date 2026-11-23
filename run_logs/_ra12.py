import json
d=json.load(open(r".spinetoolbox/project.json",encoding="utf-8"))
for k,v in d["items"].items():
    if v.get("type")=="Data Connection":
        refs=v.get("file_references",[])
        g=[r for r in refs if "geojson" in str(r).lower()]
        if g: print(k,g)
