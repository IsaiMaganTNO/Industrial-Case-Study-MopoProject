import sqlite3, collections
db = r"runs\ctryco2_mr\Final_SpineOpt_Model.tiny.3day.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(db); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_optB_probe.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
ctry = lambda z: z[:2] if z[:3] in ("NLC", "BEC") else z
conns = [r[0] for r in q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection' and e.name like '%_CO2_%'")]
xb = [n for n in conns if ctry(n.split("_CO2_")[0]) != ctry(n.split("_CO2_")[1])]
P("CO2 conns", len(conns), "cross-border", len(xb))
pairs = collections.Counter((ctry(n.split("_CO2_")[0]), ctry(n.split("_CO2_")[1])) for n in xb); P("pairs", dict(pairs))
n0 = xb[0]; P("example", n0)
for cl, nm in q("select ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name=?", n0):
    P(" rel", cl, nm)
for nm, p, v in q("select e.name, pd.name, substr(pv.value,1,80) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like ?", f"%{n0}%"):
    P(" pv", nm, p, v)
P("UC classes", [r[0] for r in q("select name from entity_class where name like '%user_constraint%'")])
uc = q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='user_constraint' limit 1")[0][0]
for cl, nm in q("select ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name=? limit 4", uc): P(" uc rel", cl, nm)
for nm, p, v in q("select e.name, pd.name, substr(pv.value,1,80) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like ? limit 8", f"%{uc}%"): P(" uc pv", nm, p, v)
# CCU users of CO2 nodes
users = collections.Counter(n.split("__")[1].rsplit("_",1)[0] for (n,) in q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='node__to_unit' and e.name like 'CO2\\_%' escape '\\'"))
P("CO2-node consumers", dict(users))
o.close()
