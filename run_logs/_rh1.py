import json
d=json.load(open(r".spinetoolbox\project.json",encoding="utf-8"))
for k in ["hydro_input","heat_input","transport_input","industry_input","cargo_input","commodity_input"]:
    v=d["items"].get(k)
    if not v: print(k,"MISSING"); continue
    print("==",k)
    for f in v.get("file_references",[]): print("   ",f["path"])
    for f in v.get("directory_references",[]): print("   DIR",f.get("path"))
