import json
d = json.load(open(".spinetoolbox/project.json", encoding="utf-8"))
print("top keys:", list(d.keys()))
for k, v in d.items():
    if k == "items":
        continue
    print("---", k, type(v).__name__, len(v) if hasattr(v, "__len__") else "")
    if isinstance(v, dict):
        print("   subkeys:", list(v.keys())[:12])
        for kk, vv in list(v.items())[:1]:
            print("   sample", kk, json.dumps(vv)[:200])
    elif isinstance(v, list) and v:
        print("   sample:", json.dumps(v[0])[:200])
