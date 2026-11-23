import sqlite3, glob
db = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]
c = sqlite3.connect(db); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_atm_probe.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
P(db)
for t in ["entity", "entity_element", "parameter_value", "entity_group", "entity_alternative", "entity_class"]:
    P(t, q(f"select sql from sqlite_master where name='{t}'"))
aid = q("select id from entity where name='atmosphere'")[0][0]; P("atm id", aid)
# direct references
P("elements", q("select ec.name, count(*) from entity_element ee join entity e on e.id=ee.entity_id join entity_class ec on ec.id=e.class_id where ee.element_id=? group by ec.name", aid))
# second-level (relations whose elements are relations touching atm)
P("lvl2", q("select ec.name, count(*) from entity_element ee join entity e on e.id=ee.entity_id join entity_class ec on ec.id=e.class_id where ee.element_id in (select entity_id from entity_element where element_id=?) group by ec.name", aid))
P("groups", q("select * from entity_group where entity_id=? or member_id=?", aid, aid))
P("ent_alt", q("select * from entity_alternative where entity_id=?", aid))
P("uf sample", q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit_flow__unit_flow' and e.name like '%atmosphere%' limit 3"))
r = q("select e.id from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit_flow__unit_flow' and e.name like '%atmosphere%' limit 1")[0][0]
P("uf elements", q("select ee.position, x.name, xc.name from entity_element ee join entity x on x.id=ee.element_id join entity_class xc on xc.id=x.class_id where ee.entity_id=? order by position", r))
P("uf count atm", q("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit_flow__unit_flow' and e.name like '%atmosphere%'"))
P("pv on rels touching atm", q("select count(*) from parameter_value where entity_id in (select entity_id from entity_element where element_id=?)", aid))
P("nodes w/o temporal link sample", q("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='node__temporal_block'"))
P("model-level defaults? node__temporal_block for atm", q("select e.name from entity e where e.name like '%atmosphere%' and e.class_id in (select id from entity_class where name like 'node__%' or name like '%__node')  and e.class_id not in (select id from entity_class where name in ('unit__to_node','node__to_unit')) limit 10"))
P("scenarios", q("select name from scenario"))
o.close()
