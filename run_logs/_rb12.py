import json
d=json.load(open(r".spinetoolbox/project.json",encoding="utf-8"))
for k,v in d["items"].items():
    if v.get("type")=="Tool" and any(s in k.lower() for s in ("heat","gas","transport","hydro","biomass","vre","industry")):
        print("###",k)
        for a in v.get("cmd_line_args",[]):
            print("    ", a.get("arg"))
