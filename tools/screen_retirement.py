r"""Feasibility screen for forced-decommissioning (retirement) patches.

Answers: "which endowed industry incumbents can I force to retire without
making the model infeasible?"

The `Scraps_EAF` failure (INFEASIBLE_OR_UNBOUNDED on the 28-unit attempt that
preceded the 26-unit Group 1 patch) teaches the actual failure mode. It was NOT
simply "no alternative exists". Three things were true at once:

  1. `steel-secondary_BEC3/BEC5` had exactly ONE feeding unit;
  2. node `demand` equalled the incumbent's endowment EXACTLY
     (0.198697288... both sides);
  3. there was no escape valve - no `balance_penalty` on the node and no
     import `connection__to_node` into it.

Point 3 is general to this model: `balance_penalty` has **1 row in the entire
DB** and there are **zero** import connections into any industry sector node.
So every sector node must be met exactly, by its own units, in its own region.
That makes the screen below necessary rather than merely prudent.

A unit is RETIRE-SAFE only if, in its own region:
  - at least one OTHER unit feeds the same sector node, AND
  - the combined `investment_count_max_cumulative` x `capacity_per_unit` of
    those others is >= the node's demand.

Checking only "has an alternative" is NOT sufficient - an alternative that is
capacity-capped below demand fails the same way. This script tests both.

Usage:
  .\.venv\Scripts\python.exe tools\screen_retirement.py <model.sqlite> [--csv out.csv]
"""
import sqlite3, json, collections, re, sys, csv

# IC1 regions plus the country-level regions of the mixed run (2026-10-09).
REG = re.compile(r"_((?:BE|NL)C\d|DE|DK|NO|UK|FR|LU)$")
# Industrial commodity nodes are discovered from the DB, NOT hardcoded. An
# earlier hand-written list of 12 sectors silently omitted 13 more families
# (plastics `chemical-PE`/`PEA` - which the ORIGINAL Group 1 patch targeted -
# plus ceramics, food, textiles, pharmaceuticals, wood, and the rest). Any
# node that is not an energy carrier and is fed by an endowed unit qualifies.
CARRIER = re.compile(
    r"^(elec|heat|cool|CO2|CH4|H2|bio|atmosphere|HC|MeOH|oil|coal|LNG|U-92"
    r"|water|waste|gas|wind|solar|nuclear|battery|hydro)")


def load(db):
    c = sqlite3.connect(db).cursor()

    def pv(par, cls):
        c.execute("""select e.name, pv.type, cast(pv.value as text)
         from parameter_value pv
         join parameter_definition pd on pd.id=pv.parameter_definition_id
         join entity e on e.id=pv.entity_id
         join entity_class ec on ec.id=pd.entity_class_id
         where pd.name=? and ec.name=?""", (par, cls))
        return {r[0]: (r[1], r[2]) for r in c.fetchall()}

    def ents(cls):
        c.execute("""select e.name from entity e
                     join entity_class ec on ec.id=e.class_id where ec.name=?""", (cls,))
        return [r[0] for r in c.fetchall()]

    return c, pv, ents


def vals(x):
    if x is None:
        return []
    t, v = x
    if t != "time_series":
        try:
            return [float(v)]
        except Exception:
            return []
    return [float(z) for z in json.loads(v).get("data", {}).values()]


def first(x):
    vs = vals(x)
    return vs[0] if vs else None


def last(x):
    vs = vals(x)
    return vs[-1] if vs else None


def screen(db):
    c, pv, ents = load(db)
    init = pv("investment_count_initial_cumulative", "unit")
    mx = pv("investment_count_max_cumulative", "unit")
    dem = pv("demand", "node")

    capu = {}
    for n, t, v in [(k,) + x for k, x in pv("capacity_per_unit", "unit__to_node").items()]:
        try:
            capu[n] = float(v)
        except Exception:
            vs = vals((t, v))
            capu[n] = vs[0] if vs else 1.0

    feeders = collections.defaultdict(list)
    for l in ents("unit__to_node"):
        p = l.split("__")
        if len(p) == 2:
            feeders[p[1]].append((p[0], l))

    rows = []
    for node in sorted(feeders):
        base = REG.sub("", node)
        if CARRIER.match(base) or node.endswith("-group"):
            continue
        us = feeders[node]
        d = first(dem.get(node)) or 0.0
        for u, link in us:
            endow = first(init.get(u)) or 0.0
            if endow <= 1e-9:
                continue
            # Already retiring? last value of the cap series is zero.
            already = (last(mx.get(u)) or 0.0) <= 1e-12
            others = [(x, ll) for x, ll in us if x != u]
            altcap = sum((last(mx.get(x)) or 0.0) * capu.get(ll, 1.0) for x, ll in others)
            if not others:
                verdict = "BLOCKED: sole producer"
            elif altcap < d - 1e-12:
                verdict = "BLOCKED: alt capacity < demand"
            else:
                verdict = "ALREADY RETIRING" if already else "RETIRE-SAFE"
            rows.append(dict(node=node, unit=u, region=(REG.search(node) or [None, None])[1]
                             if REG.search(node) else None,
                             endowment=endow, demand=d, n_alternatives=len(others),
                             alt_capacity=altcap, verdict=verdict))
    return rows


def main():
    db = sys.argv[1]
    rows = screen(db)
    w = max(len(r["unit"]) for r in rows)
    print("%-26s %-*s %10s %10s %5s %12s  %s"
          % ("sector node", w, "incumbent", "endowment", "demand", "alts", "alt_cap", "verdict"))
    for r in sorted(rows, key=lambda r: (r["verdict"], r["node"])):
        print("%-26s %-*s %10.5f %10.5f %5d %12.2f  %s"
              % (r["node"], w, r["unit"], r["endowment"], r["demand"],
                 r["n_alternatives"], r["alt_capacity"], r["verdict"]))
    cnt = collections.Counter(r["verdict"] for r in rows)
    print("\nsummary:", dict(cnt))
    if "--csv" in sys.argv:
        out = sys.argv[sys.argv.index("--csv") + 1]
        with open(out, "w", newline="", encoding="utf8") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            wr.writeheader(); wr.writerows(rows)
        print("wrote", out)


if __name__ == "__main__":
    main()
