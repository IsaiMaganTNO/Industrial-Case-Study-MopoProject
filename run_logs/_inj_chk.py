import sqlite3, glob
db = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]
c = sqlite3.connect(db); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_inj_chk.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
for u in ["CO2-injection-NSUK011_UK", "CO2-injection-NSNL012_NLC1"]:
    P("=====", u)
    for eid, cl, n in q("select e.id, ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name=?", u):
        pv = q("select pd.name, a.name, substr(pv.value,1,150) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pv.entity_id=?", eid)
        P(cl, n, pv)
# one capture unit: what does it send to atmosphere vs CO2 node
cu = [r[0] for r in q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like '%MEA_NLC5'")][:1]
for u in cu:
    P("=====", u)
    for eid, cl, n in q("select e.id, ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name=?", u):
        pv = q("select pd.name, a.name, substr(pv.value,1,150) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pv.entity_id=?", eid)
        P(cl, n, pv)
o.close()
