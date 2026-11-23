import json
d=json.load(open(r".spinetoolbox\project.json",encoding="utf8"))
it=d.get("items",{})
print("items:",len(it))
for k in ["vre_importer","power_importer","gas_import","ines_builder","ines_to_spinetop","scenario_setup","run_clustering","Run_Model_Planning"]:
    v=it.get(k)
    print(f"  {k:22} {'PRESENT' if v else 'absent':8} type={v.get('type') if v else '-'}")
spec=d.get("specifications",{})
print("\nspecifications:",{k:len(v) for k,v in spec.items()})
for s in spec.get("Tool",[])[:20]:
    print("   ",s)
