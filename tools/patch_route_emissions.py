"""Replace fuel-keyed atmosphere emissions with route-based ones for
`*-production-reference` style units that HAVE route data.

Implements S6.3 of docs/FINDING_fuel_based_emissions.md for the 15 families
identified in docs/FINDING_aluminium_and_residual_fuel_booking.md.

For each target unit:
  1. ADD/UPDATE  <unit>__atmosphere__<unit>__<outnode>  = route factor (per-year)
  2. DELETE      <unit>__atmosphere__<fuel>__<unit>     (the fuel-keyed ratio)

Step 2 is essential: leaving both would DOUBLE-BOOK carbon.

Validated convention (see run_logs/_val5.py): sheet values land in the DB
UNCONVERTED and keyed on the unit's own output, for both `tco2_t` and
`tco2_mwh` rows. Verified against CEM2-(Afm)=0.535, CEM2-(Afm)MEA=0.129,
(NG)DRI-EAF=0.651, REF-SMR-MEA=0.002 - all exact matches.
"""
import argparse, json, re, shutil, sqlite3, sys
import pandas as pd

SHEET = r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
CARBON = {"coal", "CH4", "HC", "crude", "waste"}
# families that are genuine fuel-burners - never touch
KEEP_FUEL = {"SCPC-existing", "coal-boiler-existing", "oil-boiler-existing",
             "oil-eng", "oil-eng-existing", "wasteST-existing"}
YEARS = ["2030", "2040", "2050"]
STAMP = {"2030": "2030-01-01T00:00:00", "2040": "2041-01-01T00:00:00",
         "2050": "2050-01-01T00:00:00"}

def base(n):
    # IC1 regions (BEC1..NLC9) AND country-level regions of the mixed run.
    # The original pattern matched IC1 only, so `_DE/_DK/_NO/_UK` units were
    # silently skipped ("no route data") - found 2026-10-09.
    return re.sub(r'_((NL|BE)C\d+|DE|DK|NO|UK|FR|LU)$', '', n)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    df = pd.ExcelFile(SHEET).parse("ind_process_routes_co2_emission")
    df["Industry"] = df["Industry"].astype(str)
    # The sheet holds BOTH co2_emission and co2_capture rows keyed on the same
    # Industry name. Only co2_emission belongs on the `atmosphere` flow ratio;
    # without this filter a capture row can silently overwrite an emission row.
    df = df[df["emission"].astype(str) == "co2_emission"]
    factors = {}
    for _, r in df.iterrows():
        factors[r["Industry"]] = {y: float(r[y]) for y in ["2030", "2040", "2050"]}

    if not a.dry_run:
        shutil.copyfile(a.src, a.dst)
    con = sqlite3.connect(a.src if a.dry_run else a.dst)

    xb_before = xborder(con)

    # classify every unit's atmosphere ratios
    rows = con.execute("""
        SELECT e.id, e.name, pv.id FROM entity e
        JOIN entity_class ec ON ec.id=e.class_id
        JOIN parameter_value pv ON pv.entity_id=e.id
        JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
        WHERE ec.name='unit_flow__unit_flow'
          AND pd.name='flow_ratio_equality_coefficient'
          AND e.name LIKE '%__atmosphere__%'""").fetchall()
    fuelkeyed, routekeyed = {}, set()
    for eid, name, pvid in rows:
        p = name.split("__")
        if len(p) < 4: continue
        unit, key = p[0], base(p[2])
        if key in CARBON:
            fuelkeyed.setdefault(unit, []).append((eid, name, pvid))
        else:
            routekeyed.add(unit)

    # output node per unit
    outnode = {}
    for (n,) in con.execute("""SELECT e.name FROM entity e
        JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='unit__to_node'"""):
        u, nd = n.split("__", 1)
        if nd != "atmosphere":
            outnode[u] = nd

    targets, skipped = [], []
    for unit, lst in fuelkeyed.items():
        fam = base(unit)
        if unit in routekeyed:  continue          # already route-based
        if fam in KEEP_FUEL:    skipped.append((unit, "genuine fuel burner")); continue
        if fam not in factors:  skipped.append((unit, "no route data")); continue
        if unit not in outnode: skipped.append((unit, "no output node")); continue
        targets.append((unit, fam, lst))

    # ---- PASS 2: routes with NO atmosphere link at all -------------------
    # The loop above can only see units that ALREADY had some atmosphere ratio.
    # A route carrying a non-zero sheet factor but no `<unit>__atmosphere` link
    # is invisible to it and silently emits nothing. This is exactly how
    # `aluminium-primary-production-alternative` (1.4447 tCO2/t, and the ONLY
    # aluminium route running in 2050) kept a false zero after the first patch.
    # For these we must also CREATE the unit__to_node(unit, atmosphere) entity.
    orphans = []
    seen = set(fuelkeyed) | routekeyed
    for unit, nd in outnode.items():
        fam = base(unit)
        if unit in seen:        continue
        if fam in KEEP_FUEL:    continue
        if fam not in factors:  continue
        if max(factors[fam][y] for y in YEARS) <= 0.0:
            continue                               # genuinely zero-carbon route
        orphans.append((unit, fam, []))

    print("fuel-keyed units: %d | already route-based: %d" % (len(fuelkeyed), len(routekeyed)))
    print("TARGETS: %d   skipped: %d   ORPHANS(new links): %d"
          % (len(targets), len(skipped), len(orphans)))
    ofams = {}
    for u, f, _ in orphans: ofams[f] = ofams.get(f, 0) + 1
    if ofams:
        print("\n%-56s %6s %10s" % ("orphan family (was emitting NOTHING)", "units", "2050"))
        for f, c in sorted(ofams.items()):
            print("%-56s %6d %10.4f" % (f[:56], c, factors[f]["2050"]))
    targets = targets + orphans

    fams = {}
    for u, f, _ in targets: fams[f] = fams.get(f, 0) + 1
    print("\n%-52s %6s %10s" % ("family", "units", "2050 t/unit"))
    for f, c in sorted(fams.items()):
        print("%-52s %6d %10.4f" % (f[:52], c, factors[f]["2050"]))

    if a.dry_run:
        print("\nDRY RUN - nothing written."); return

    cls = con.execute("SELECT id FROM entity_class WHERE name='unit_flow__unit_flow'").fetchone()[0]
    pdid = con.execute("""SELECT id FROM parameter_definition
        WHERE name='flow_ratio_equality_coefficient' AND entity_class_id=?""", (cls,)).fetchone()[0]
    altid = con.execute("SELECT id FROM alternative WHERE name='Base'").fetchone()[0]

    # unit__to_node: needed to CREATE missing <unit>__atmosphere links (orphans)
    u2ncls = con.execute("SELECT id FROM entity_class WHERE name='unit__to_node'").fetchone()[0]
    u2ndims = con.execute("""SELECT dimension_id, position FROM entity_class_dimension
        WHERE entity_class_id=? ORDER BY position""", (u2ncls,)).fetchall()
    assert len(u2ndims) == 2, "unit__to_node dims %r" % (u2ndims,)
    udim, ndim = u2ndims[0][0], u2ndims[1][0]
    atm = con.execute("SELECT id FROM entity WHERE name='atmosphere' AND class_id=?",
                      (ndim,)).fetchone()
    assert atm, "atmosphere node not found"
    atmid = atm[0]


    # dimensions of unit_flow__unit_flow (both are the `unit_flow` superclass)
    dims = con.execute("""SELECT dimension_id, position FROM entity_class_dimension
        WHERE entity_class_id=? ORDER BY position""", (cls,)).fetchall()
    assert len(dims) == 2, "expected 2 dimensions, got %r" % (dims,)
    dim0, dim1 = dims[0][0], dims[1][0]

    added = deleted = links = 0
    for unit, fam, lst in targets:
        nd = outnode[unit]
        ename = "%s__atmosphere__%s__%s" % (unit, unit, nd)
        payload = {"type": "map", "index_type": "date_time", "rank": 1,
                   "data": {STAMP[y]: factors[fam][y] for y in YEARS}}
        blob = sqlite3.Binary(json.dumps(payload).encode("utf-8"))

        # ensure unit__to_node(unit, atmosphere) exists - orphans lack it
        a2n = "%s__atmosphere" % unit
        got = con.execute("SELECT id FROM entity WHERE name=? AND class_id=?",
                          (a2n, u2ncls)).fetchone()
        if got is None:
            uent = con.execute("SELECT id FROM entity WHERE name=? AND class_id=?",
                               (unit, udim)).fetchone()
            if uent is None:
                sys.exit("ABORT: unit entity %s not found" % unit)
            lid = con.execute("SELECT COALESCE(MAX(id),0)+1 FROM entity").fetchone()[0]
            con.execute("INSERT INTO entity (id,class_id,name) VALUES (?,?,?)",
                        (lid, u2ncls, a2n))
            con.execute("""INSERT INTO entity_element
                (entity_id,entity_class_id,position,element_id,dimension_id)
                VALUES (?,?,?,?,?)""", (lid, u2ncls, 0, uent[0], udim))
            con.execute("""INSERT INTO entity_element
                (entity_id,entity_class_id,position,element_id,dimension_id)
                VALUES (?,?,?,?,?)""", (lid, u2ncls, 1, atmid, ndim))
            links += 1

        eid = con.execute("SELECT id FROM entity WHERE name=? AND class_id=?",
                          (ename, cls)).fetchone()
        if eid is None:
            u2n = con.execute("""SELECT id FROM entity WHERE name=? AND class_id=?""",
                              (a2n, u2ncls)).fetchone()
            o2n = con.execute("""SELECT id FROM entity WHERE name=? AND class_id=?""",
                              ("%s__%s" % (unit, nd), u2ncls)).fetchone()
            if not (u2n and o2n):
                sys.exit("ABORT: missing unit__to_node for %s" % unit)
            newid = con.execute("SELECT COALESCE(MAX(id),0)+1 FROM entity").fetchone()[0]
            con.execute("INSERT INTO entity (id,class_id,name) VALUES (?,?,?)",
                        (newid, cls, ename))
            con.execute("""INSERT INTO entity_element
                (entity_id,entity_class_id,position,element_id,dimension_id)
                VALUES (?,?,?,?,?)""", (newid, cls, 0, u2n[0], dim0))
            con.execute("""INSERT INTO entity_element
                (entity_id,entity_class_id,position,element_id,dimension_id)
                VALUES (?,?,?,?,?)""", (newid, cls, 1, o2n[0], dim1))
            eid = (newid,)
        con.execute("""INSERT INTO parameter_value
            (entity_id,entity_class_id,parameter_definition_id,alternative_id,value,type)
            VALUES (?,?,?,?,?,'map')""", (eid[0], cls, pdid, altid, blob))
        added += 1
        for _, _, pvid in lst:
            con.execute("DELETE FROM parameter_value WHERE id=?", (pvid,))
            deleted += 1

    con.commit()
    xb_after = xborder(con)
    assert abs(xb_after - xb_before) < 1e-9, "cross-border changed!"
    print("\nADDED route rows    : %d" % added)
    print("DELETED fuel rows   : %d" % deleted)
    print("NEW atmosphere links: %d" % links)
    print("GUARD cross-border: %.3f (unchanged)" % xb_after)
    con.close()


def xborder(con):
    rows = con.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
        JOIN entity e ON e.id=pv.entity_id
        JOIN entity_class ec ON ec.id=e.class_id
        WHERE pd.name='investment_count_initial_cumulative' AND ec.name='connection'""").fetchall()
    assert rows, "cross-border guard found 0 rows"
    t = 0.0
    for (v,) in rows:
        try: t += float(v)
        except Exception: pass
    return t

main()
