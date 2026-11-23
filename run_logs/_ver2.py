import sqlite3,json,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
CARBON={"coal","CH4","HC","crude","waste"}
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
rows=c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
JOIN parameter_value pv ON pv.entity_id=e.id
JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
WHERE ec.name='unit_flow__unit_flow' AND pd.name='flow_ratio_equality_coefficient'
AND e.name LIKE '%__atmosphere__%'""").fetchall()
fk,rk={},set()
for (n,) in rows:
    p=n.split("__")
    if len(p)<4: continue
    (fk.setdefault(p[0],[]).append(n) if base(p[2]) in CARBON else rk.add(p[0]))
print("fuel-keyed:",len(fk)," route-keyed:",len(rk))
print("DOUBLE-BOOKED:",len(set(fk)&rk))
fam={}
for u in fk: fam[base(u)]=fam.get(base(u),0)+1
print("residual fuel families:",sorted(fam.items()))
print("\naluminium alternative atmosphere entities:")
for (n,) in c.execute("SELECT e.name FROM entity e WHERE e.name LIKE '%aluminium-primary-production-alternative%' AND e.name LIKE '%atmosphere%'"):
    print("  ",n)
q="""SELECT typeof(pv.value),cast(pv.value as text) FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
WHERE e.name LIKE 'aluminium-primary-production-alternative%__atmosphere__%'"""
for t,v in c.execute(q): print("  type=",t,v[:110])
