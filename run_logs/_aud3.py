import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
CARBON={"coal","CH4","HC","crude","waste"}
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
# units consuming a carbon fuel
cons={}
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit'"""):
    nd,u=n.split("__",1)
    if base(nd) in CARBON: cons.setdefault(u,set()).add(base(nd))
# units with any atmosphere booking
booked=set()
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  JOIN parameter_value pv ON pv.entity_id=e.id
  WHERE ec.name='unit_flow__unit_flow' AND e.name LIKE '%__atmosphere__%'"""):
    booked.add(n.split("__")[0])
gap={}
for u,f in cons.items():
    if u not in booked: gap.setdefault(base(u),set()).update(f)
print("families consuming CARBON fuel but with NO atmosphere booking:",len(gap))
for k,v in sorted(gap.items()): print("  %-46s %s"%(k[:46],sorted(v)))
