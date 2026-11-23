"""Reduce the mixed-resolution model to NL+BE (IC1) with the original border stubs.
Rule (reference = the old 17-region model REF, used only for structure and non-regional data):
  keep entity e of SRC  iff  e exists in REF  or  (e touches a BE/NL IC1 region and no DE/DK/NO/UK/AT.. token)
  non-regional entities (stubs, atmosphere, temporal blocks, groups, model) -> parameters copied from REF
  BE/NL regional entities -> parameters kept from SRC (current data)
  REF-only non-regional entities (stub node__temporal_block) -> added
Usage: reduce_to_nlbe.py SRC REF DST
"""
import sys, shutil, os, re
from spinedb_api import DatabaseMapping
src, ref, dst = sys.argv[1:4]
if os.path.exists(dst): sys.exit(f"{dst} exists")
NB = re.compile(r"(BE|NL)C\d|NS(NL|BE)\d")
FOR = re.compile(r"(?<![A-Za-z0-9])(DE|DK|NO|UK|AT|CH|CZ|IE|PL|SE|FI)(?![A-Za-z0-9])|(?:NS|AS|AT|BS)(DE|DK|NO|UK)")
url = lambda p: "sqlite:///" + os.path.abspath(p).replace("\\", "/")
def read(p):
    E, V = {}, {}
    with DatabaseMapping(url(p)) as m:
        for e in m.get_entity_items(): E[(e["entity_class_name"], tuple(e["entity_byname"]))] = e
        for v in m.get_parameter_value_items():
            V[(v["entity_class_name"], tuple(v["entity_byname"]), v["parameter_definition_name"], v["alternative_name"])] = (v["type"], v["value"])
    return set(E), V
RE, RV = read(ref)
shutil.copy(src, dst)
nreg = lambda k: NB.search("__".join(k[1])) is None
with DatabaseMapping(url(dst)) as m:
    SE = {(e["entity_class_name"], tuple(e["entity_byname"])): e for e in m.get_entity_items()}
    drop = [k for k in SE if k not in RE and not (NB.search("__".join(k[1])) and not FOR.search("__".join(k[1])))]
    # drop multi-dimensional first is not needed: remove_items cascades
    ids = [int(SE[k]["id"]) if not hasattr(SE[k]["id"],"db_id") else int(SE[k]["id"].db_id) for k in drop]
print("dropping entities", len(ids))
import sqlite3
con = sqlite3.connect(dst); con.execute("PRAGMA foreign_keys=ON")
con.execute("CREATE TEMP TABLE d(id INTEGER PRIMARY KEY)"); con.executemany("INSERT INTO d VALUES(?)", [(i,) for i in ids])
before = con.execute("select count(*) from entity").fetchone()[0]
con.execute("DELETE FROM entity WHERE id IN (SELECT id FROM d)"); con.commit()
after = con.execute("select count(*) from entity").fetchone()[0]
print("entities", before, "->", after, "(incl. cascaded relationships)")
con.close()
with DatabaseMapping(url(dst)) as m:
    # add REF-only non-regional entities (0-dim first)
    cur = {(e["entity_class_name"], tuple(e["entity_byname"])) for e in m.get_entity_items()}
    add = sorted((k for k in RE - cur if nreg(k)), key=lambda k: len(k[1]))
    for c, bn in add:
        m.add_item("entity", entity_class_name=c, entity_byname=bn)
    m.commit_session("reduce: restore stub entities")
    print("added entities", len(add), sorted({k[0] for k in add}))
    # replace params on non-regional entities by REF
    cur = {(e["entity_class_name"], tuple(e["entity_byname"])) for e in m.get_entity_items()}
    rm = [int(getattr(v["id"],"db_id",v["id"])) for v in m.get_parameter_value_items() if nreg((v["entity_class_name"], tuple(v["entity_byname"])))]
    m.commit_session("noop") if False else None
m = None
con = sqlite3.connect(dst); con.execute("CREATE TEMP TABLE r(id INTEGER PRIMARY KEY)"); con.executemany("INSERT INTO r VALUES(?)", [(i,) for i in rm])
con.execute("DELETE FROM parameter_value WHERE id IN (SELECT id FROM r)"); con.commit(); con.close()
with DatabaseMapping(url(dst)) as m:
    cur = {(e["entity_class_name"], tuple(e["entity_byname"])) for e in m.get_entity_items()}
    n = 0
    for (c, bn, p, a), (t, val) in RV.items():
        if (c, bn) in cur and nreg((c, bn)):
            m.add_item("parameter_value", entity_class_name=c, entity_byname=bn, parameter_definition_name=p, alternative_name=a, type=t, value=val); n += 1
    m.commit_session("reduce: non-regional params from REF")
    print("non-regional params replaced", len(rm), "->", n)
print("WROTE", dst)



