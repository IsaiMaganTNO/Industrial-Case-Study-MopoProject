import json
d=json.load(open(r".spinetoolbox/project.json",encoding="utf-8"))
for k,v in d["items"].items():
    if "power" in k.lower():
        print("###",k,v.get("type"),v.get("specification"))
        for a in v.get("cmd_line_args",[]): print("   ",a)
        for r in v.get("file_references",[]): print("   ref",r)
