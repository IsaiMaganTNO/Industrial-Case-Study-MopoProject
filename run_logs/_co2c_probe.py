import sys; sys.stdout = open(r'run_logs\_co2c_probe.out', 'w', encoding='utf8')
import sqlite3, glob
db = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]; print(db)
c = sqlite3.connect(db)
q = lambda s, *a: c.execute(s, a).fetchall()
ents = q("select e.id, ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id where lower(e.name) like '%atmos%' or lower(e.name) like '%co2%'")
for i, cl, n in ents:
    if cl in ("node", "commodity", "user_constraint", "unit") or "atmos" in n.lower():
        pv = q("select pd.name, a.name, length(pv.value), substr(pv.value,1,80) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pv.entity_id=?", i)
        if pv or "atmos" in n.lower(): print(cl, n, pv[:12])
n = q("select count(*) from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name like '%tmosph%'")
print("relations touching atmosphere:", n)
rel = q("select ec.name, count(*) from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id where x.name like '%tmosph%' group by ec.name")
print(rel)

