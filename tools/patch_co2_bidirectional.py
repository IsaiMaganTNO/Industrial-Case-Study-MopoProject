r"""Mirror every CO2 pipeline connection so the network is bidirectional.

WHY
---
docs/FINDING_co2_network_unidirectional.md: the source sheet
CO2_data_IC1.xlsx!network lists each corridor ONCE (171 rows = 171 undirected
pairs, 0 reverse twins) and carries a symmetric `km` + distance-proportional
`tariff`, i.e. it is an UNDIRECTED edge list. ines_target.py writes one
directional INES link per row and never adds the reverse, so CO2 is the only
commodity in the model with 0 reverse twins (CH4 has 88/91, H2 88/89).
Consequence: CO2_BEC6 has NO out-edges and CO2_BEC7 cannot reach any injector,
making Belgian CCS infeasible rather than uneconomic.

WHAT
----
For each existing connection `A_CO2_B`, create `B_CO2_A` mirroring the exact
structure of the forward link (verified against the CH4 convention):
  connection             B_CO2_A
  connection__from_node  B_CO2_A__CO2_B   + connection_flow_cost (same tariff)
  connection__to_node    B_CO2_A__CO2_A
  connection__node__node B_CO2_A__CO2_A__CO2_B + fix_ratio_out_in_connection_flow

Tariff is copied unchanged: it is distance-proportional and distance is
symmetric.

SAFETY
------
- Operates on a COPY; SRC and DST are positional.
- --dry-run prints the plan and writes nothing.
- Skips any reverse that already exists (idempotent).
- Does NOT touch electricity/cross-border connections: the only entities
  created have '_CO2_' in the name. The cross-border guard
  (investment_count_initial_cumulative on class `connection`, 327 rows,
  sum 1522.505) is asserted unchanged at the end.
"""
import sqlite3, shutil, sys, os

CLS_CONN, CLS_FROM, CLS_TO, CLS_NNN = 1, 16, 20, 53
DIM_CONN, DIM_NODE = 1, 5
PD_FLOW_COST_FROM = 35          # connection_flow_cost on connection__from_node
PD_FIX_RATIO      = 48          # fix_ratio_out_in_connection_flow on conn__node__node
ALT_BASE = 1

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry  = "--dry-run" in sys.argv
    if len(args) != 2:
        print(__doc__); print("usage: patch_co2_bidirectional.py SRC DST [--dry-run]")
        return 1
    src, dst = args
    if not dry:
        if os.path.abspath(src) == os.path.abspath(dst):
            print("refusing to patch in place"); return 1
        shutil.copyfile(src, dst)
        print(f"copied {src} -> {dst}")
    db = dst if not dry else src
    c = sqlite3.connect(db)

    # Resolve ids by NAME (hard-coded values were for the 17-region build and are
    # not guaranteed to hold after a rebuild). Fail loudly if any differ.
    global CLS_CONN, CLS_FROM, CLS_TO, CLS_NNN, DIM_CONN, DIM_NODE, PD_FLOW_COST_FROM, PD_FIX_RATIO, ALT_BASE
    cid = lambda n: c.execute("select id from entity_class where name=?", (n,)).fetchone()[0]
    CLS_CONN, CLS_FROM, CLS_TO, CLS_NNN = cid("connection"), cid("connection__from_node"), \
        cid("connection__to_node"), cid("connection__node__node")
    DIM_CONN, DIM_NODE = CLS_CONN, cid("node")
    pid = lambda n, k: c.execute("select id from parameter_definition where name=? and entity_class_id=?",
                                 (n, k)).fetchone()[0]
    PD_FLOW_COST_FROM = pid("connection_flow_cost", CLS_FROM)
    PD_FIX_RATIO = pid("fix_ratio_out_in_connection_flow", CLS_NNN)
    ALT_BASE = c.execute("select id from alternative where name='Base'").fetchone()[0]
    print(f"ids: conn={CLS_CONN} from={CLS_FROM} to={CLS_TO} nnn={CLS_NNN} node={DIM_NODE} "
          f"cost={PD_FLOW_COST_FROM} ratio={PD_FIX_RATIO} Base={ALT_BASE}")

    guard_before = c.execute("""
        select count(*), coalesce(sum(cast(pv.value as text)+0),0) from parameter_value pv
        join parameter_definition pd on pd.id=pv.parameter_definition_id
        join entity e on e.id=pv.entity_id
        where pd.name='investment_count_initial_cumulative' and e.class_id=?""",(CLS_CONN,)).fetchone()

    conns = {n: i for i, n in c.execute(
        "select id,name from entity where class_id=? and name like '%!_CO2!_%' escape '!'",(CLS_CONN,))}
    print(f"CO2 connections found: {len(conns)}")

    node_id = {n: i for i, n in c.execute("select id,name from entity where class_id=?",(5,))} \
        if False else {}
    # resolve node ids by name via entity table (nodes are class 5 members as dimension)
    for i, n in c.execute("select id,name from entity where name like 'CO2!_%' escape '!'"):
        node_id[n] = i

    commit_id = c.execute("select max(commit_id) from entity").fetchone()[0]
    made = {"conn":0,"from":0,"to":0,"nnn":0,"cost":0,"ratio":0,"skip":0}

    def new_entity(cls, name):
        cur = c.execute("insert into entity(class_id,name,description,commit_id) values(?,?,NULL,?)",
                        (cls, name, commit_id))
        return cur.lastrowid

    def add_el(eid, cls, elem, dim, pos):
        c.execute("""insert into entity_element
            (entity_id,entity_class_id,element_id,dimension_id,position) values(?,?,?,?,?)""",
            (eid, cls, elem, dim, pos))

    def add_pv(pd_id, eid, cls, val):
        # type MUST be 'float' to match every existing row; NULL makes the Spine
        # reader fall back to type inference and can silently drop the value.
        c.execute("""insert into parameter_value
            (parameter_definition_id,entity_id,entity_class_id,type,value,commit_id,alternative_id)
            values(?,?,?,'float',?,?,?)""", (pd_id, eid, cls, sqlite3.Binary(val), commit_id, ALT_BASE))

    for fwd, fid in sorted(conns.items()):
        a, _, b = fwd.partition("_CO2_")
        rev = f"{b}_CO2_{a}"
        if rev in conns:
            made["skip"] += 1; continue
        na, nb = f"CO2_{a}", f"CO2_{b}"
        if na not in node_id or nb not in node_id:
            print(f"  !! missing node for {fwd}"); continue
        # tariff from the forward from_node row
        cost = c.execute("""select pv.value from parameter_value pv
            join entity e on e.id=pv.entity_id
            join entity_element el on el.entity_id=e.id and el.position=0
            where e.class_id=? and el.element_id=? and pv.parameter_definition_id=?""",
            (CLS_FROM, fid, PD_FLOW_COST_FROM)).fetchone()
        ratio = c.execute("""select pv.value from parameter_value pv
            join entity e on e.id=pv.entity_id
            join entity_element el on el.entity_id=e.id and el.position=0
            where e.class_id=? and el.element_id=? and pv.parameter_definition_id=?""",
            (CLS_NNN, fid, PD_FIX_RATIO)).fetchone()
        if dry:
            print(f"  + {rev:22s} from {nb} to {na}  cost={cost and bytes(cost[0])[:12]}")
            made["conn"] += 1; continue

        rid = new_entity(CLS_CONN, rev); add_el(rid, CLS_CONN, rid, DIM_CONN, 0) if False else None
        made["conn"] += 1
        # from_node: (rev, CO2_b)
        fe = new_entity(CLS_FROM, f"{rev}__{nb}")
        add_el(fe, CLS_FROM, rid, DIM_CONN, 0); add_el(fe, CLS_FROM, node_id[nb], DIM_NODE, 1)
        made["from"] += 1
        if cost: add_pv(PD_FLOW_COST_FROM, fe, CLS_FROM, bytes(cost[0])); made["cost"] += 1
        # to_node: (rev, CO2_a)
        te = new_entity(CLS_TO, f"{rev}__{na}")
        add_el(te, CLS_TO, rid, DIM_CONN, 0); add_el(te, CLS_TO, node_id[na], DIM_NODE, 1)
        made["to"] += 1
        # node__node: (rev, CO2_a[out], CO2_b[in])
        ne = new_entity(CLS_NNN, f"{rev}__{na}__{nb}")
        add_el(ne, CLS_NNN, rid, DIM_CONN, 0)
        add_el(ne, CLS_NNN, node_id[na], DIM_NODE, 1)
        add_el(ne, CLS_NNN, node_id[nb], DIM_NODE, 2)
        made["nnn"] += 1
        if ratio: add_pv(PD_FIX_RATIO, ne, CLS_NNN, bytes(ratio[0])); made["ratio"] += 1

    if dry:
        print(f"\nDRY RUN - would create {made['conn']} reverse connections "
              f"({made['skip']} already present). Nothing written."); return 0

    c.commit()
    guard_after = c.execute("""
        select count(*), coalesce(sum(cast(pv.value as text)+0),0) from parameter_value pv
        join parameter_definition pd on pd.id=pv.parameter_definition_id
        join entity e on e.id=pv.entity_id
        where pd.name='investment_count_initial_cumulative' and e.class_id=?""",(CLS_CONN,)).fetchone()
    total = c.execute("select count(*) from entity where class_id=? and name like '%!_CO2!_%' escape '!'",
                      (CLS_CONN,)).fetchone()[0]
    print("\ncreated:", made)
    print(f"CO2 connections now: {total}")
    print(f"cross-border guard before={guard_before} after={guard_after}")
    assert guard_before == guard_after, "CROSS-BORDER GUARD CHANGED - ABORT"
    print("guard OK (unchanged)")

    # --- self-checks: every created row must be indistinguishable in SHAPE from
    # --- the pre-existing forward links. Catches silent-ignore failure modes.
    problems = []
    t = c.execute("""select distinct pv.type from parameter_value pv
        join parameter_definition pd on pd.id=pv.parameter_definition_id
        where pd.name in ('connection_flow_cost','fix_ratio_out_in_connection_flow')""").fetchall()
    if len(t) != 1 or t[0][0] != "float":
        problems.append(f"parameter_value.type not uniformly 'float': {t}")
    dup = c.execute("select count(*) from (select class_id,name from entity group by 1,2 having count(*)>1)").fetchone()[0]
    if dup: problems.append(f"{dup} duplicate (class,name)")
    off = c.execute("""select count(*) from entity e where e.class_id=? and e.name like '%!_CO2!_%' escape '!'
        and ((select count(*) from entity x join entity_element el on el.entity_id=x.id and el.position=0
              where x.class_id=? and el.element_id=e.id)<>1
          or (select count(*) from entity x join entity_element el on el.entity_id=x.id and el.position=0
              where x.class_id=? and el.element_id=e.id)<>1
          or (select count(*) from entity x join entity_element el on el.entity_id=x.id and el.position=0
              where x.class_id=? and el.element_id=e.id)<>1)""",
        (CLS_CONN, CLS_FROM, CLS_TO, CLS_NNN)).fetchone()[0]
    if off: problems.append(f"{off} CO2 connections with wrong from/to/node__node counts")
    if problems:
        print("\n*** SELF-CHECK FAILED ***")
        for p in problems: print("   -", p)
        return 1
    print("self-checks OK (type/dup/arity)")
    print("integrity:", c.execute("pragma integrity_check").fetchone()[0])
    return 0

if __name__ == "__main__":
    sys.exit(main())
