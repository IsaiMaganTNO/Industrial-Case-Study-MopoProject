import sqlite3, pickle, pandas as pd
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
caps={}
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where pd.name='investment_count_total_max_cumulative' and ec.name='investment_group'
  and (e.name like 'wind-on%' or e.name like 'solar-PV%')"""):
    try: caps[n]=float(bytes(v).decode())
    except Exception: pass
d=pickle.load(open(r"run_logs\gascap.pkl","rb"))
fl=d["fleet"]
def used(prefix,ctry):
    s=fl[fl.tech.str.startswith(prefix)&fl.region.str.startswith(ctry)&(fl.year==2050)]
    return s["units"].sum()
print(f"{'group':18s} {'cap now':>9s} {'x0.15':>9s} {'2050 used':>10s} {'binds?':>8s}")
for pre,lab in [("wind-on","wind-on"),("solar-PV","solar-PV")]:
    for ctry in ["BEC","NLC"]:
        tot=sum(v for k,v in caps.items() if k.startswith(pre) and ctry in k)
        u=used(pre,ctry)
        print(f"{lab+'_'+ctry:18s} {tot:9.2f} {tot*0.15:9.2f} {u:10.2f} {'YES' if u>tot*0.15 else 'no':>8s}")
