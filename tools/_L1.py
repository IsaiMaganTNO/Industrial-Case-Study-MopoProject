import sqlite3, json
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
alts={r[0]:r[1] for r in c.execute("SELECT id,name FROM alternative")}
TECH=["bioST","wind-on-SP277-HH100","wind-off-FB-SP370-HH155","solar-PV-no-tracking","solar-PV-tracking"]
PAR=["unit_investment_cost","fom_cost","vom_cost","capacity_per_unit","unit_availability_factor",
     "lifetime_economic","investment_count_max_cumulative","discount_rate","unit_capacity"]
q="""SELECT e.name, pd.name, pv.alternative_id, pv.type, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name IN (%s)""" % ",".join("?"*len(PAR))
for n,p,a,t,v in c.execute(q,PAR):
    base=n.split("__")[0]
    tech=base.rsplit("_",1)[0]
    if tech not in TECH and not any(base.startswith(x) for x in TECH): continue
    if "_NLC6" not in n and "_NSNL011" not in n and "_NLC6_" not in n: continue
    v=v.decode() if isinstance(v,bytes) else v
    print(f"{n[:50]:50s} {p[:28]:28s} {alts.get(a,a)[:8]:8s} {v[:52]}")
