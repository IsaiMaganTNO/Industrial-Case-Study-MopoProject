import json
d=json.load(open(r"data/Energy_Conversion/config.json"))
print("geolevel:", d.get("geolevel"), "| euroyear", d.get("euroyear"), "| refyear", d.get("referenceyear"))
