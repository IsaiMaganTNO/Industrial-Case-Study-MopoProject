import sqlite3,pandas as pd,json,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
cap=pd.read_excel(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx",
                  sheet_name="ind_process_routes_co2_capture")
cap=cap[cap["2050"]>0]
def val(v):
    try:
        d=json.loads(bytes(v).decode()) if isinstance(v,bytes) else json.loads(v)
        d=d.get("data",d); return list(d.values())[-1]
    except Exception:
        try: return float(v)
        except Exception: return None
bad=ok=0
for _,r in cap.iterrows():
    fam=str(r["Industry"]); want=float(r["2050"])
    row=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ? AND e.name LIKE '%__CO2%'
      LIMIT 1""",(fam+"\\_%",)).fetchone()
    if row is None:
        row=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ? AND e.name LIKE '%__CO2%'
          LIMIT 1""",(fam+"_%",)).fetchone()
    if row is None: print("NO DB ROW  %-24s want %.4f"%(fam[:24],want)); bad+=1; continue
    got=val(row[0])
    if got is None or abs(got-want)>1e-4: print("MISMATCH   %-24s want %.4f got %s"%(fam[:24],want,got)); bad+=1
    else: ok+=1
print("match=%d mismatch/missing=%d"%(ok,bad))
