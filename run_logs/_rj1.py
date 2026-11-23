import yaml,io
for lab,p in [("IC1",r"data-pipelines\europe\userconfig.yaml"),("EU",r"EU_case\data-pipelines\europe\userconfig.yaml")]:
    d=yaml.safe_load(open(p,encoding="utf-8"))
    m=d.get("model",{})
    print("==",lab)
    print("   units:",m.get("units"))
    print("   planning_years:",m.get("planning_years"))
    print("   type:",m.get("type"),"ops_res:",m.get("operations_resolution"),"plan_res:",m.get("planning_resolution"))
    pl=d.get("pipelines",{})
    for k in ["heat_sector","transport_sector","industrial_sector","other_industrial_sector"]:
        print("   %-24s %s"%(k,pl.get(k)))
    print("   countries:",d.get("countries"))
