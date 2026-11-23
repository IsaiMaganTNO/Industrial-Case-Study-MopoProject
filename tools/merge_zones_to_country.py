"""Merge NL/BE zone network nodes (<carrier>_(BE|NL)C<k>) into country nodes <carrier>_(BE|NL).
Steps: delete intra-country connections; keep lowest zone node per (carrier,country) and rename;
re-point other zone nodes' relationship elements; drop duplicate node__temporal_block; sum demand
time series per country/alternative; regenerate relationship names; delete merged zone nodes.
Usage: merge_zones_to_country.py SRC DST
"""
import sys, os, re, shutil, sqlite3, json, collections
src, dst = sys.argv[1:3]
if os.path.exists(dst): sys.exit(f"{dst} exists")
shutil.copy(src, dst)
con = sqlite3.connect(dst); con.execute("PRAGMA foreign_keys=ON")
q = lambda s, *a: con.execute(s, a).fetchall()
def delete_entities(ids):
    """delete entities plus all relationships that (recursively) use them as elements"""
    ids = set(ids); fr = set(ids)
    while fr:
        nxt = {r[0] for r in q("select distinct entity_id from entity_element where element_id in (%s)" % ",".join(map(str, fr)))} - ids
        ids |= nxt; fr = nxt
    con.executemany("delete from entity where id=?", [(i,) for i in ids]); return len(ids)
cid = {n: i for i, n in q("select id,name from entity_class")}
PAT = re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_((BE|NL)C(\d+))$")
nodes = {}
for i, n in q("select id,name from entity where class_id=?", cid["node"]):
    m = PAT.match(n)
    if m: nodes[i] = (m.group(1), m.group(3), int(m.group(4)), n)
grp = collections.defaultdict(list)
for i, (c, k, z, n) in nodes.items(): grp[(c, k)].append((z, i))
keep = {key: min(v)[1] for key, v in grp.items()}
target = {i: keep[(c, k)] for i, (c, k, z, n) in nodes.items()}
print("zone nodes", len(nodes), "-> country nodes", len(keep))
# 1 intra-country connections
INTRA = re.compile(r"^((BE|NL)C\d+)_\w+_((BE|NL)C\d+)$")
ic = [i for i, n in q("select id,name from entity where class_id=?", cid["connection"])
      if (m := INTRA.match(n)) and m.group(2) == m.group(4)]
print("intra connections deleted", len(ic), "incl. relationships", delete_entities(ic))
# 2 demand: sum per (country node, alternative)
did = q("select id from parameter_definition where name='demand' and entity_class_id=?", cid["node"])[0][0]
acc = {}
for eid, alt, typ, val in q("select entity_id,alternative_id,type,value from parameter_value where parameter_definition_id=?", did):
    if eid not in nodes: continue
    assert typ == "time_series", typ
    d = json.loads(val); key = (target[eid], alt)
    if key not in acc: acc[key] = d; acc[key]["data"] = list(d["data"]); acc[key]["_n"] = 1
    else:
        a = acc[key]; assert a["index"] == d["index"] and len(a["data"]) == len(d["data"])
        a["data"] = [x + y for x, y in zip(a["data"], d["data"])]; a["_n"] += 1
for (t, alt), d in acc.items():
    n = d.pop("_n")
    con.execute("update parameter_value set value=? where entity_id=? and alternative_id=? and parameter_definition_id=?",
                (json.dumps(d).encode(), t, alt, did))
    print("demand", nodes[t][3], "alt", alt, "zones summed", n, "total", round(sum(d["data"]), 3))
# 3 check node params of merged nodes equal to kept (other than demand)
for i in nodes:
    if target[i] == i: continue
    a = set(q("select parameter_definition_id,alternative_id,value from parameter_value where entity_id=? and parameter_definition_id<>?", i, did))
    b = set(q("select parameter_definition_id,alternative_id,value from parameter_value where entity_id=? and parameter_definition_id<>?", target[i], did))
    assert a == b, (nodes[i][3], a ^ b)
# 4 node__temporal_block duplicates
ntb = cid["node__temporal_block"]
rows = q("select ee.entity_id,ee.element_id,(select element_id from entity_element x where x.entity_id=ee.entity_id and x.position=1) from entity_element ee join entity e on e.id=ee.entity_id where e.class_id=? and ee.position=0", ntb)
dropntb = []
for eid, nd, tb in rows:
    if nd in nodes and target[nd] != nd:
        k = [r for r in rows if r[1] == target[nd] and r[2] == tb][0][0]
        pa = set(q("select parameter_definition_id,alternative_id,value from parameter_value where entity_id=?", eid))
        pb = set(q("select parameter_definition_id,alternative_id,value from parameter_value where entity_id=?", k))
        assert pa == pb; dropntb.append(eid)
assert delete_entities(dropntb) == len(dropntb)
print("node__temporal_block dropped", len(dropntb))
# 5 re-point elements
n = 0
for i in nodes:
    if target[i] != i:
        n += con.execute("update entity_element set element_id=? where element_id=?", (target[i], i)).rowcount
print("elements re-pointed", n)
# 6 rename kept nodes, delete merged
for (c, k), i in keep.items(): con.execute("update entity set name=? where id=?", (f"{c}_{k}", i))
rm = [i for i in nodes if target[i] != i]
left = q("select count(*) from entity_element where element_id in (%s)" % ",".join(map(str, rm)))[0][0]
assert left == 0, left
con.executemany("delete from entity where id=?", [(i,) for i in rm])
print("zone nodes deleted", len(rm))
# 7 regenerate multi-dim names (iterate until stable: unit_flow__unit_flow depends on unit__to_node names)
for it in range(3):
    multi = q("select id,class_id,name from entity where id in (select distinct entity_id from entity_element)")
    names = {r[0]: r[2] for r in q("select id,class_id,name from entity")}
    els = collections.defaultdict(list)
    for e, x in q("select entity_id,element_id from entity_element order by entity_id,position"): els[e].append(x)
    new = {e: "__".join(names[x] for x in els[e]) for e, c, o in multi}
    cnt = collections.Counter((c, new[e]) for e, c, o in multi)
    dup = [k for k, v in cnt.items() if v > 1]
    assert not dup, dup[:5]
    chg = [(e, new[e]) for e, c, o in multi if new[e] != o]
    con.executemany("update entity set name=? where id=?", [(f"__tmp_{e}", e) for e, _ in chg])
    con.executemany("update entity set name=? where id=?", [(n, e) for e, n in chg])
    print("renamed pass", it, len(chg))
    if not chg: break
con.commit()
print("fk_check", q("PRAGMA foreign_key_check")[:5])
con.execute("VACUUM"); con.close()
print("WROTE", dst)

