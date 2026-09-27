import sys, collections
from spinedb_api import DatabaseMapping

DBS = {
    "IC1": r".spinetoolbox\items\final_spineopt_model\Final_SpineOpt_Model.sqlite",
    "EU":  r"EU_case\.spinetoolbox\items\final_spineopt_model\Final_SpineOpt_Model.sqlite",
}

out = open("tools/_cmp_out.txt", "w", encoding="utf-8")
def w(*a):
    print(*a, file=out)

summary = {}
for tag, path in DBS.items():
    with DatabaseMapping("sqlite:///" + path) as db:
        ents = collections.Counter()
        for e in db.query(db.entity_sq):
            ents[e.class_id] += 1
        cls = {c.id: c.name for c in db.query(db.entity_class_sq)}
        ent_by_class = collections.Counter({cls[k]: v for k, v in ents.items()})

        pv = collections.Counter()
        for p in db.query(db.parameter_definition_sq):
            pv[p.id] = p.name
        vals = collections.Counter()
        for v in db.query(db.parameter_value_sq):
            vals[pv.get(v.parameter_definition_id, "?")] += 1
        summary[tag] = (ent_by_class, vals)
        w(f"=== {tag} : {sum(ent_by_class.values())} entities, {sum(vals.values())} values")

ic_e, ic_v = summary["IC1"]
eu_e, eu_v = summary["EU"]

w("\n--- ENTITY CLASSES present in EU but MISSING/EMPTY in IC1 ---")
for name, n in eu_e.most_common():
    if ic_e.get(name, 0) == 0:
        w(f"  {name:45s} EU={n:7d}  IC1=0")

w("\n--- PARAMETERS present in EU but MISSING in IC1 ---")
for name, n in eu_v.most_common():
    if ic_v.get(name, 0) == 0:
        w(f"  {name:45s} EU={n:7d}  IC1=0")

w("\n--- PARAMETERS in IC1 but not EU ---")
for name, n in ic_v.most_common():
    if eu_v.get(name, 0) == 0:
        w(f"  {name:45s} IC1={n:7d}  EU=0")

w("\n--- COVERAGE RATIO (values per entity), shared params, biggest gaps ---")
ic_tot = sum(ic_e.values()); eu_tot = sum(eu_e.values())
rows = []
for name in set(ic_v) & set(eu_v):
    ic_r = ic_v[name] / ic_tot
    eu_r = eu_v[name] / eu_tot
    if eu_r > 0:
        rows.append((ic_r / eu_r, name, ic_v[name], eu_v[name]))
rows.sort()
for ratio, name, a, b in rows[:25]:
    w(f"  {name:45s} IC1={a:7d} EU={b:7d}  rel-coverage={ratio:.2f}")
out.close()
