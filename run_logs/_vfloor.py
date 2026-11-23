import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
caps={}
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where pd.name='investment_count_total_max_cumulative' and ec.name='investment_group'
  and (e.name like 'wind-on%' or e.name like 'solar-PV%')"""):
    caps[n]=float(bytes(v).decode())
HIST={"wind-on":{"BE":3.6,"NL":7.2},"solar-PV":{"BE":11.6,"NL":33.5}}
F=0.15
for tech in ["wind-on","solar-PV"]:
    for ctry in ["BE","NL"]:
        grp={k:v for k,v in caps.items() if k.startswith(tech+"_") and k.split("_")[1].startswith(ctry)}
        tot=sum(grp.values()); hist=HIST[tech][ctry]
        litA=sum(max(v*F,hist) for v in grp.values())        # buggy: national floor per region
        pro ={k:hist*v/tot for k,v in grp.items()}            # pro-rata disaggregated floor
        litB=sum(max(v*F,pro[k]) for k,v in grp.items())
        print(f"{tech:9s} {ctry}: cap {tot:7.2f} | x0.15 {tot*F:6.2f} | nat hist {hist:5.1f}")
        print(f"            literal(per-region national floor) -> {litA:7.2f} GW  <-- the documented bug")
        print(f"            pro-rata floor                      -> {litB:7.2f} GW  <-- faithful to intent")
