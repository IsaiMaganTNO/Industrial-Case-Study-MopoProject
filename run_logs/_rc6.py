import json, io
P=r".spinetoolbox/project.json"
raw=open(P,encoding="utf-8").read()
SUBS=[
 ("geodata/IC1.geojson","geodata/IC1_NWEU.geojson"),
 ("data/Rdemand/other_electricity_demand_IC1.csv","data/Rdemand/other_electricity_demand_IC1_NWEU.csv"),
 ("data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx","data/Gas/Gas_Sectors_Dataset.xlsx"),
 ("data/VRE/VRE_time_series","data/VRE_NWEU/VRE_time_series"),
 ("data/VRE/VRE_installed_capacities_2020_and_2025","data/VRE_NWEU/VRE_installed_capacities_2020_and_2025"),
 ("data/VRE/VRE_greenfield_installation_potentials","data/VRE_NWEU/VRE_greenfield_installation_potentials"),
 ("data/VRE/VRE_costs_EUR2025","data/VRE_NWEU/VRE_costs_EUR2025"),
]
for old,new in SUBS:
    n=raw.count(old)
    print("%-58s occurrences=%d" % (old,n))
    assert n>0, old
for old,new in SUBS:
    raw=raw.replace(old,new)
json.loads(raw)   # validate
open(P,"w",encoding="utf-8").write(raw)
print("\nwritten, valid JSON")
d=json.load(open(P,encoding="utf-8"))
for k in ["power_importer","rdemand_importer","gas_import","VRE_importer"]:
    print("\n###",k)
    for a in d["items"][k]["cmd_line_args"]:
        print("   ", a.get("arg"))
