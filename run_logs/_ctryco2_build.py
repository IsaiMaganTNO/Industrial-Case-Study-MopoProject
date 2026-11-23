import sqlite3, glob, shutil, os, json, collections
src = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]
os.makedirs(r"runs\ctryco2_mr", exist_ok=True)
dst = r"runs\ctryco2_mr\Final_SpineOpt_Model.tiny.3day.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite"
shutil.copyfile(src, dst)
c = sqlite3.connect(dst); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_ctryco2_build.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
E1990 = {"NL": 221.78, "BE": 145.84, "NO": 50.71, "DE": 1251, "DK": 71.82, "UK": 806.3}
tot = sum(E1990.values()); share = {k: v / tot for k, v in E1990.items()}
def ctry(z):
    for p in ("NLC", "BEC"):
        if z.startswith(p): return p[:2]
    assert z in E1990, z; return z
node_cls = q("select id from entity_class where name='node'")[0][0]
atm = q("select id from entity where name='atmosphere' and class_id=?", node_cls)[0][0]
pvs = q("select parameter_definition_id, entity_class_id, type, value, alternative_id from parameter_value where entity_id=?", atm)
new = {}
for k in E1990:
    c.execute("insert into entity(class_id, name) values(?,?)", (node_cls, f"atmosphere_{k}"))
    nid = c.execute("select last_insert_rowid()").fetchone()[0]; new[k] = nid
    for pd_, ec, ty, val, alt in pvs:
        name = q("select name from parameter_definition where id=?", pd_)[0][0]
        if name == "storage_investment_count_max_cumulative":
            d = json.loads(val); d["data"] = {t: x * share[k] for t, x in d["data"].items()}; val = json.dumps(d).encode()
        elif name == "storage_investment_count_initial_cumulative":
            val = json.dumps(float(val) * share[k]).encode()
        c.execute("insert into parameter_value(parameter_definition_id, entity_id, entity_class_id, type, value, alternative_id) values(?,?,?,?,?,?)", (pd_, nid, ec, ty, val, alt))
# repoint relations
rels = q("select e.id, e.name, ee.position from entity_element ee join entity e on e.id=ee.entity_id where ee.element_id=?", atm)
cnt = collections.Counter()
for rid, rname, pos in rels:
    unit = rname.replace("atmosphere__", "").replace("__atmosphere", "")
    k = ctry(unit.rsplit("_", 1)[-1]); cnt[(k, "in" if pos == 0 else "out")] += 1
    c.execute("update entity_element set element_id=? where entity_id=? and element_id=?", (new[k], rid, atm))
    c.execute("update entity set name=? where id=?", (rname.replace("atmosphere", f"atmosphere_{k}"), rid))
# rename unit_flow__unit_flow entities for consistency
for rid, rname in q("select e.id, e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit_flow__unit_flow' and e.name like '%__atmosphere__%'"):
    parts = [x[0] for x in q("select x.name from entity_element ee join entity x on x.id=ee.element_id where ee.entity_id=? order by position", rid)]
    c.execute("update entity set name=? where id=?", ("__".join(parts), rid))
left = q("select count(*) from entity_element where element_id=?", atm)[0][0]; P("refs left on old atm", left)
c.execute("delete from parameter_value where entity_id=?", (atm,)); c.execute("delete from entity where id=?", (atm,))
c.commit()
P("relation counts (country, atm->unit=in / unit->atm=out)", dict(cnt))
P("shares", {k: round(v, 4) for k, v in share.items()})
for k, nid in new.items():
    P(k, q("select pd.name, substr(pv.value,1,200) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where entity_id=? and pd.name like 'storage_investment_count%'", nid))
o.close()
