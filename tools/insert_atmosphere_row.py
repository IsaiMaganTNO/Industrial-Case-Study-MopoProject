"""Insert a unit->atmosphere emission row into a built SpineOpt model DB.

Structural proof-of-concept for the "correct fix". Units burning a secondary
carrier (HC_*, CH4_*, MeOH_*) have no emission row because process_emissions()
only keys on the 4 global fuel nodes that carry co2_content.

For unit U with fuel F we must create:
  1. entity  unit__to_node        (U, atmosphere)
  2. entity  unit_flow__unit_flow (U, atmosphere, F, U)
         dim0 -> unit__to_node (U, atmosphere)
         dim1 -> node__to_unit (F, U)
  3. parameter_value flow_ratio_equality_coefficient on (2), alternative Base

Naming convention observed in the DB:
    unit__to_node         "<unit>__<node>"
    unit_flow__unit_flow  "<unit>__<outnode>__<innode>__<unit>"
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path

CLS_U2N = "unit__to_node"
CLS_N2U = "node__to_unit"
CLS_UFUF = "unit_flow__unit_flow"
PARAM = "flow_ratio_equality_coefficient"


def class_id(con, name):
    r = con.execute("SELECT id FROM entity_class WHERE name = ?", (name,)).fetchone()
    if r is None:
        raise SystemExit("entity_class %s missing" % name)
    return r[0]


def entity_id(con, cls_id, name):
    r = con.execute("SELECT id FROM entity WHERE class_id = ? AND name = ?", (cls_id, name)).fetchone()
    return r[0] if r else None


_next_id = [None]


def next_entity_id(con):
    """Running counter.

    MAX(id)+1 alone is wrong for bulk use: in dry-run nothing is written, and
    even with --apply several ids may be handed out before the first INSERT
    lands, so repeated calls would collide. Seed once, then increment.
    """
    if _next_id[0] is None:
        _next_id[0] = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM entity").fetchone()[0]
    else:
        _next_id[0] += 1
    return _next_id[0]


def ensure_u2n(con, unit, node, apply_):
    cid = class_id(con, CLS_U2N)
    name = "%s__%s" % (unit, node)
    eid = entity_id(con, cid, name)
    if eid is not None:
        print("  exists  %-20s %s (id=%d)" % (CLS_U2N, name, eid))
        return eid
    u_id = entity_id(con, class_id(con, "unit"), unit)
    n_id = entity_id(con, class_id(con, "node"), node)
    if u_id is None or n_id is None:
        raise SystemExit("unit %r or node %r not found" % (unit, node))
    eid = next_entity_id(con)
    print("  CREATE  %-20s %s (id=%d)" % (CLS_U2N, name, eid))
    if apply_:
        con.execute("INSERT INTO entity (id, class_id, name, description, commit_id) VALUES (?,?,?,NULL,NULL)", (eid, cid, name))
        pairs = ((u_id, class_id(con, "unit")), (n_id, class_id(con, "node")))
        for pos, (el, dim) in enumerate(pairs):
            con.execute("INSERT INTO entity_element (entity_id, entity_class_id, element_id, dimension_id, position) VALUES (?,?,?,?,?)", (eid, cid, el, dim, pos))
    return eid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--unit", required=True)
    ap.add_argument("--fuel", required=True)
    ap.add_argument("--coeff", type=float, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup", action="store_true")
    args = ap.parse_args()

    if args.apply and args.backup:
        bak = Path(args.db).with_suffix(".preinsert.sqlite")
        shutil.copy2(args.db, bak)
        print("backup written: %s" % bak)

    con = sqlite3.connect(args.db)
    # Spine ships its DBs with foreign_keys OFF and *relies* on it: a
    # unit_flow__unit_flow declares both dimensions as the `unit_flow`
    # SUPERCLASS (class 14), but the entity_element rows actually point at
    # unit__to_node / node__to_unit entities (classes 44/45). Turning FK
    # enforcement on makes that legitimate indirection fail. Match the DB.
    con.execute("PRAGMA foreign_keys = OFF")

    cid_ufuf = class_id(con, CLS_UFUF)
    cid_n2u = class_id(con, CLS_N2U)
    dim_id = con.execute("SELECT dimension_id FROM entity_class_dimension WHERE entity_class_id = ? AND position = 0", (cid_ufuf,)).fetchone()[0]

    print("unit=%s fuel=%s coeff=%g" % (args.unit, args.fuel, args.coeff))

    atm_id = ensure_u2n(con, args.unit, "atmosphere", args.apply)

    n2u_name = "%s__%s" % (args.fuel, args.unit)
    n2u_id = entity_id(con, cid_n2u, n2u_name)
    if n2u_id is None:
        raise SystemExit("node__to_unit %r not found - unit does not burn this fuel" % n2u_name)
    print("  exists  %-20s %s (id=%d)" % (CLS_N2U, n2u_name, n2u_id))

    uf_name = "%s__atmosphere__%s__%s" % (args.unit, args.fuel, args.unit)
    uf_id = entity_id(con, cid_ufuf, uf_name)
    if uf_id is None:
        uf_id = next_entity_id(con)
        print("  CREATE  %-20s %s (id=%d)" % (CLS_UFUF, uf_name, uf_id))
        if args.apply:
            con.execute("INSERT INTO entity (id, class_id, name, description, commit_id) VALUES (?,?,?,NULL,NULL)", (uf_id, cid_ufuf, uf_name))
            for pos, el in ((0, atm_id), (1, n2u_id)):
                con.execute("INSERT INTO entity_element (entity_id, entity_class_id, element_id, dimension_id, position) VALUES (?,?,?,?,?)", (uf_id, cid_ufuf, el, dim_id, pos))
    else:
        print("  exists  %-20s %s (id=%d)" % (CLS_UFUF, uf_name, uf_id))

    pd_id = con.execute("SELECT id FROM parameter_definition WHERE name = ? AND entity_class_id = ?", (PARAM, cid_ufuf)).fetchone()[0]
    alt_id = con.execute("SELECT id FROM alternative WHERE name = 'Base'").fetchone()[0]
    have = con.execute("SELECT id FROM parameter_value WHERE parameter_definition_id = ? AND entity_id = ? AND alternative_id = ?", (pd_id, uf_id, alt_id)).fetchone()
    blob = repr(float(args.coeff)).encode()
    if have:
        print("  UPDATE  %s = %g" % (PARAM, args.coeff))
        if args.apply:
            con.execute("UPDATE parameter_value SET value = ?, type = 'float' WHERE id = ?", (blob, have[0]))
    else:
        print("  CREATE  %s = %g" % (PARAM, args.coeff))
        if args.apply:
            pv_id = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM parameter_value").fetchone()[0]
            con.execute("INSERT INTO parameter_value (id, parameter_definition_id, entity_id, entity_class_id, type, value, commit_id, alternative_id) VALUES (?,?,?,?,'float',?,NULL,?)", (pv_id, pd_id, uf_id, cid_ufuf, blob, alt_id))

    if args.apply:
        con.commit()
        print("committed")
    else:
        print("DRY RUN - nothing written")
    con.close()


if __name__ == "__main__":
    main()
