import sqlite3,pandas as pd,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
x=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
cap=pd.read_excel(x,sheet_name="ind_process_routes_co2_capture")
nz=cap[cap["2050"]>0]["Industry"].astype(str).tolist()
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
# which units have a CO2 output flow (capture represented)?
has=set()
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit__to_node'"""):
    u,nd=n.split("__",1)
    if base(nd)=="CO2": has.add(base(u))
miss=[f for f in nz if f not in has]
print("families with non-zero capture in sheet:",len(nz))
print("of those, MISSING a CO2 output node in DB:",len(miss))
for f in miss[:20]: print("   ",f)
