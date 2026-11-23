import sqlite3, shutil, os
src = r"runs\ctryco2_mr\Final_SpineOpt_Model.tiny.3day.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite"
os.makedirs(r"runs\ctryco2B_mr", exist_ok=True)
dst = r"runs\ctryco2B_mr\Final_SpineOpt_Model.tiny.3day.ctryco2B_mr_ccslow_ccu_cap16_dac0.sqlite"
shutil.copyfile(src, dst)
c = sqlite3.connect(dst); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_ctryco2B_build.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
ctry = lambda z: z[:2] if z[:3] in ("NLC", "BEC") else z
cls = {n: i for i, n in q("select id, name from entity_class")}
dims = {cid: [d for d, in q("select dimension_id from entity_class_dimension where entity_class_id=? order by position", cid)] for cid in cls.values()}
eid = {(cid, n): i for i, cid, n in q("select id, class_id, name from entity")}
def ent(cname, elems):
    cid = cls[cname]; name = "__".join(elems)
    if (cid, name) in eid: return eid[(cid, name)]
    c.execute("insert into entity(class_id, name) values(?,?)", (cid, name)); i = c.execute("select last_insert_rowid()").fetchone()[0]
    for pos, (d, e) in enumerate(zip(dims[cid], elems)):
        c.execute("insert into entity_element(entity_id, entity_class_id, element_id, dimension_id, position) values(?,?,?,?,?)", (i, cid, eid[(d, e)], d, pos))
    eid[(cid, name)] = i; return i
pd_ratio = q("select id from parameter_definition where name='fix_ratio_out_in_connection_flow'")[0][0]
base = q("select id from alternative where name='Base'")[0][0]
tmpl = q("select type, value from parameter_value where parameter_definition_id=? limit 1", pd_ratio)[0]
P("ratio template", tmpl)
conns = [n for n, in q("select e.name from entity e where class_id=? and name like '%\\_CO2\\_%' escape '\\'", cls["connection"])]
n = 0
for cn in conns:
    a, b = cn.split("_CO2_"); A, B = ctry(a), ctry(b)
    if A == B: continue
    ent("connection__from_node", [cn, f"atmosphere_{A}"])
    ent("connection__to_node", [cn, f"atmosphere_{B}"])
    for out_n, in_n in [(f"atmosphere_{B}", f"CO2_{a}"), (f"atmosphere_{B}", f"atmosphere_{A}")]:
        r = ent("connection__node__node", [cn, out_n, in_n])
        c.execute("insert into parameter_value(parameter_definition_id, entity_id, entity_class_id, type, value, alternative_id) values(?,?,?,?,?,?)", (pd_ratio, r, cls["connection__node__node"], tmpl[0], b"1.0", base))
    n += 1
c.commit(); P("cross-border conns wired", n)
P("new rels", q("select ec.name, count(*) from entity e join entity_class ec on ec.id=e.class_id where e.name like '%\\_CO2\\_%__atmosphere\\_%' escape '\\' group by ec.name"))
o.close()
