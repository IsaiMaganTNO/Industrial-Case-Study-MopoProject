import pandas as pd, sqlite3, collections
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
model=collections.defaultdict(float)
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where ec.name='investment_group' and pd.name='investment_count_total_max_cumulative'
    and (e.name like 'solar-PV%' or e.name like 'wind-on%')"""):
    try: val=float(bytes(v).decode())
    except: continue
    model[(("solar-PV" if n.startswith("solar") else "wind-on"), n.split("_")[-1])]=val
for lbl,p in [("solar-PV",r"data\VRE\VRE_greenfield_installation_potentials\potential_solar-PV.xlsx"),
              ("wind-on", r"data\VRE\VRE_greenfield_installation_potentials\potential_wind-on.xlsx")]:
    d=pd.ExcelFile(p).parse("Data")
    d=d[d["Region"].astype(str).str.match(r'^(BE|NL)C\d+$',na=False)]
    print(f"\n=== {lbl}: SOURCE vs MODEL (GW)")
    print(f"{'region':8s} {'source':>10s} {'model':>10s} {'ratio':>8s}")
    tb=tn=mb=mn=0.0
    for _,r in d.iterrows():
        reg=r["Region"]; s=float(r["Greenfield_potential_GW"]); m=model.get((lbl,reg),float('nan'))
        print(f"{reg:8s} {s:10.4f} {m:10.4f} {m/s if s else 0:8.4f}")
        if reg.startswith("BE"): tb+=s; mb+=m
        else: tn+=s; mn+=m
    print(f"{'BE tot':8s} {tb:10.4f} {mb:10.4f} {mb/tb:8.4f}")
    print(f"{'NL tot':8s} {tn:10.4f} {mn:10.4f} {mn/tn:8.4f}")
