"""Compare two SpineOpt databases: entities, parameter values (per alternative) and scenarios.

Usage: python tools/compare_model_dbs.py A.sqlite B.sqlite [--tol 1e-9] [--show 20]
Exit code 0 when identical within tolerance, 1 otherwise.
"""
import argparse, json, math, sqlite3, sys
from collections import Counter

def load(path):
    c = sqlite3.connect(path); q = lambda s: c.execute(s).fetchall()
    ents = {(cl, n) for cl, n in q("select ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id")}
    pv = {}
    for cl, en, pd, al, typ, val in q("""select ec.name, e.name, pd.name, a.name, pv.type, pv.value from parameter_value pv
            join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
            join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id"""):
        pv[(cl, en, pd, al)] = (typ, bytes(val) if val is not None else None)
    scen = set(q("""select s.name, a.name, sa.rank from scenario_alternative sa join scenario s on s.id=sa.scenario_id
            join alternative a on a.id=sa.alternative_id"""))
    return ents, pv, scen

def same(x, y, tol):
    if x == y: return True
    try:
        vx, vy = json.loads(x[1]), json.loads(y[1])
    except Exception:
        return False
    def eq(u, v):
        if isinstance(u, (int, float)) and isinstance(v, (int, float)):
            return math.isclose(u, v, rel_tol=tol, abs_tol=1e-12)
        if isinstance(u, dict) and isinstance(v, dict):
            return u.keys() == v.keys() and all(eq(u[k], v[k]) for k in u)
        if isinstance(u, list) and isinstance(v, list):
            return len(u) == len(v) and all(eq(p, r) for p, r in zip(u, v))
        return u == v
    return eq(vx, vy)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--tol", type=float, default=1e-9); ap.add_argument("--show", type=int, default=20)
    a = ap.parse_args()
    ea, pa, sa = load(a.a); eb, pb, sb = load(a.b)
    ok = True
    def report(title, items):
        nonlocal ok
        items = sorted(items)
        print(f"{title}: {len(items)}")
        if items:
            ok = False
            print("   by class/parameter:", Counter(i[0] if len(i) == 2 else (i[0], i[2]) for i in items).most_common(8))
            for i in items[:a.show]: print("   ", i)
    print(f"A {a.a}\nB {a.b}")
    print(f"entities A {len(ea)}  B {len(eb)} | parameter values A {len(pa)}  B {len(pb)}")
    report("entities only in A", ea - eb)
    report("entities only in B", eb - ea)
    report("values only in A", set(pa) - set(pb))
    report("values only in B", set(pb) - set(pa))
    diff = [k for k in set(pa) & set(pb) if not same(pa[k], pb[k], a.tol)]
    report("values that differ", diff)
    report("scenario rows only in A", sa - sb)
    report("scenario rows only in B", sb - sa)
    print("IDENTICAL" if ok else "DIFFERENT")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
