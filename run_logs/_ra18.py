import json, collections
p = r"data/Energy_Conversion/config.json"
raw = open(p, encoding="utf-8").read()
d = json.loads(raw, object_pairs_hook=collections.OrderedDict)
assert d["geolevel"] == "PECD1", d["geolevel"]
d["geolevel"] = "IC1"
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=4))
chk = json.load(open(p, encoding="utf-8"))
print("geolevel now:", chk["geolevel"])
print("units_new n =", len(chk["units_new"]), "bioST+CC in list:", "bioST+CC" in chk["units_new"])
print("units_existing n =", len(chk["units_existing"]))
