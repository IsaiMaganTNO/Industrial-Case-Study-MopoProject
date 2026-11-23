import sqlite3, glob, json, collections
db = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]
c = sqlite3.connect(db); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_co2c_sum.out", "w", encoding="utf8")
P = lambda *a: print(*a, file=o)
for pd_, al, v in q("select pd.name, a.name, pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id join entity e on e.id=pv.entity_id where e.name='atmosphere'"):
    P("ATM", pd_, al, v[:400])
rel = q("select ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name='atmosphere'")
cnt = collections.Counter(cl for cl, _ in rel); P("REL", dict(cnt))
reg = collections.Counter()
for cl, n in rel:
    if cl == "unit__to_node":
        u = n.rsplit("__", 1)[0]; reg[u.rsplit("_", 1)[-1]] += 1
P("emitters by region suffix", dict(reg))
P("CO2-ish nodes", [r[0] for r in q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='node' and (e.name like 'CO2%' or e.name like '%tmos%')")])
P("user_constraints", [r[0] for r in q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='user_constraint'")])
P("UC params", [r[0] for r in q("select pd.name from parameter_definition pd join entity_class ec on ec.id=pd.entity_class_id where ec.name like '%user_constraint%' and pd.name like '%coefficient%'")][:40])
P("node params co2/emis", [r[0] for r in q("select pd.name from parameter_definition pd join entity_class ec on ec.id=pd.entity_class_id where ec.name='node' and (pd.name like '%co2%' or pd.name like '%emission%' or pd.name like '%storage_investment_count_max%')")])
o.close()
