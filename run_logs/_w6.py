import sqlite3,pandas as pd,json,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
em=pd.read_excel(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx",
                 sheet_name="ind_process_routes_co2_emission")
em=em[em["2050"]>0]
def val(v):
    try:
        d=json.loads(bytes(v).decode()) if isinstance(v,bytes) else json.loads(v)
        d=d.get("data",d); return list(d.values())[-1]
    except Exception:
        try: return float(v)
        except Exception: return None
bad=ok=0; missing=[]
for _,r in em.iterrows():
    fam=str(r["Industry"]); want=float(r["2050"])
    row=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ? AND e.name LIKE '%atmosphere%'
      LIMIT 1""",(fam+"_%",)).fetchone()
    if row is None: missing.append((fam,want)); bad+=1; continue
    got=val(row[0])
    if got is None or abs(got-want)>1e-4: print("MISMATCH %-30s want %.4f got %s"%(fam[:30],want,got)); bad+=1
    else: ok+=1
print("emission rows w/ 2050>0: %d  match=%d  problem=%d"%(len(em),ok,bad))
for f,w in missing: print("   NO ATM ROW %-40s %.4f"%(f[:40],w))
