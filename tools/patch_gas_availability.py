r"""Constrain fossil gas supply: LNG availability 0.50, NL gas extraction 0.0.

WHY
---
docs/FINDING_gas_volumes_and_transit.md + docs/PROPOSAL_reduce_gas_supply.md.

1. LNG-terminal and gas-extraction have NO availability_factor, so they run at a
   100% load factor every hour of every year. Observed supply equals nameplate
   x 8760 EXACTLY in all 17 regions (BE saturated in all three milestones, NL by
   2050). Methane consumption rises 434 -> 624 -> 662 TWh, about 1.3x present-day
   NL+BE inland demand, in a deeply-decarbonised scenario.

2. The ceiling derives from ALSI/ENTSOG TERMINAL SEND-OUT, a transit-capable
   ENTRY capacity that in reality also serves Germany and re-export. Using it as
   a ceiling on DOMESTIC supply lets inland demand draw on transit headroom.
   (Measured: in-model net exchange at CH4_DE/FR/UK/LU is EXACTLY 0.0 TWh, so
   none of the 662 TWh is transit - the contamination is in the input capacity.)

3. gas-extraction represents genuine domestic production (a `unit` drawing from
   the fossil-CH4 commodity and booking 0.2 upstream CO2 to atmosphere) - NOT
   storage withdrawal, which is the separate CH4-geo-formation node. Its
   284.5 GWh/d is a static 2025-vintage figure. The Groningen field closed in
   October 2023, so NL production should not be available in ANY modelled year.

WHAT
----
Adds `availability_factor` (parameter_definition 217 on class `unit`, default
1.0, "acting as a multiplier on its capacity_per_unit") in alternative Base:
  * 17 x LNG-terminal_*    -> 0.50
  *  9 x gas-extraction_*  -> 0.00   (closed in every year)

Resulting 2050 ceiling: BE 122.1 + NL 157.0 = ~279 TWh (was 662.1).

CAVEAT
------
0.50 is a judgement, not a derived value. Real EU LNG terminal utilisation is
broadly ~40-65%, but that benchmark is not sourced here; if ENTSOG/ALSI send-out
profiles become available a time series should replace the flat factor.
This caps SUPPLY and does not fix demand-side oddities (the 2050 gas-boiler
rebuild, DAC burning 81.7 TWh of methane) - it may MASK them.

SAFETY
------
- Operates on a COPY; SRC and DST are positional.
- --dry-run prints the plan and writes nothing.
- Idempotent: updates the row if it already exists rather than duplicating.
- type is written as "float" on every row (a NULL type makes the Spine reader
  fall back to inference and can SILENTLY DROP the value).
- Touches ONLY units named LNG-terminal_* / gas-extraction_*. No electricity or
  cross-border component is modified; the cross-border guard
  (investment_count_initial_cumulative on class `connection`, 327 rows,
  sum 1522.5048) is asserted unchanged.
"""
import sqlite3, shutil, sys, os

CLS_UNIT = 13
PD_AVAIL = 217   # 17-region baseline value; re-resolved by NAME in main()
ALT_BASE = 1
CLS_CONN = 1
GUARD_ROWS, GUARD_SUM = 327, 1522.5048   # checked only with --expect-guard

# Mixed-resolution decision (2026-10-08): LNG 0.50 in ALL regions; extraction
# zeroed for NL ONLY (Groningen closed). NO/UK/DE/DK extraction left untouched -
# those countries still produce.
TARGETS = [("LNG-terminal_%", 0.50), ("gas-extraction_NL%", 0.00)]


def guard(c):
    return c.execute(
        "select count(*), coalesce(sum(cast(pv.value as text)+0),0) "
        "from parameter_value pv "
        "join parameter_definition pd on pd.id=pv.parameter_definition_id "
        "join entity e on e.id=pv.entity_id "
        "where pd.name=? and e.class_id=?",
        ("investment_count_initial_cumulative", CLS_CONN)).fetchone()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 2:
        print(__doc__)
        print("usage: patch_gas_availability.py SRC DST [--dry-run]")
        return 1
    src, dst = args
    if not dry:
        if os.path.abspath(src) == os.path.abspath(dst):
            print("refusing to patch in place")
            return 1
        shutil.copyfile(src, dst)
        print("copied " + src + " -> " + dst)
    db = src if dry else dst
    c = sqlite3.connect(db)

    global CLS_UNIT, PD_AVAIL, ALT_BASE, CLS_CONN
    CLS_UNIT = c.execute("select id from entity_class where name='unit'").fetchone()[0]
    CLS_CONN = c.execute("select id from entity_class where name='connection'").fetchone()[0]
    PD_AVAIL = c.execute("select id from parameter_definition where name='availability_factor' "
                         "and entity_class_id=?", (CLS_UNIT,)).fetchone()[0]
    ALT_BASE = c.execute("select id from alternative where name='Base'").fetchone()[0]
    print("ids: unit=%s connection=%s availability_factor=%s Base=%s"
          % (CLS_UNIT, CLS_CONN, PD_AVAIL, ALT_BASE))

    g_before = guard(c)
    print("cross-border guard before: " + str(g_before))
    if "--expect-guard" in sys.argv and (
            g_before[0] != GUARD_ROWS or abs(g_before[1] - GUARD_SUM) > 1e-6):
        print("UNEXPECTED BASELINE GUARD " + str(g_before) + " - ABORT")
        return 1
    others = [n for (n,) in c.execute(
        "select name from entity where class_id=? and name like 'gas-extraction%' "
        "and name not like 'gas-extraction_NL%' order by name", (CLS_UNIT,))]
    print("gas-extraction left UNTOUCHED (%d): %s" % (len(others), ", ".join(others)))

    commit_id = c.execute("select max(commit_id) from entity").fetchone()[0]
    made = {"insert": 0, "update": 0}

    for pat, val in TARGETS:
        units = list(c.execute(
            "select id,name from entity where class_id=? and name like ? order by name",
            (CLS_UNIT, pat)))
        print("\n" + pat + " -> availability_factor = " + str(val)
              + "  (" + str(len(units)) + " units)")
        if not units:
            print("   *** NO UNITS MATCHED - ABORT ***")
            return 1
        blob = sqlite3.Binary(repr(float(val)).encode())
        for uid, nm in units:
            row = c.execute(
                "select id from parameter_value where parameter_definition_id=? "
                "and entity_id=? and alternative_id=?",
                (PD_AVAIL, uid, ALT_BASE)).fetchone()
            if dry:
                made["update" if row else "insert"] += 1
                continue
            if row:
                c.execute("update parameter_value set value=?, type=? where id=?",
                          (blob, "float", row[0]))
                made["update"] += 1
            else:
                c.execute(
                    "insert into parameter_value(parameter_definition_id,entity_id,"
                    "entity_class_id,type,value,commit_id,alternative_id) "
                    "values(?,?,?,?,?,?,?)",
                    (PD_AVAIL, uid, CLS_UNIT, "float", blob, commit_id, ALT_BASE))
                made["insert"] += 1
        print("   " + ", ".join(n for _, n in units[:3]) + " ...")

    if dry:
        print("\nDRY RUN - nothing written. plan: " + str(made))
        return 0

    c.commit()
    print("\nrows: " + str(made))

    problems = []
    g_after = guard(c)
    if g_after != g_before:
        problems.append("cross-border guard changed " + str(g_before) + " -> " + str(g_after))

    for pat, val in TARGETS:
        rows = list(c.execute(
            "select e.name, pv.value, pv.type from parameter_value pv "
            "join entity e on e.id=pv.entity_id "
            "where pv.parameter_definition_id=? and e.class_id=? and e.name like ?",
            (PD_AVAIL, CLS_UNIT, pat)))
        n_expected = c.execute(
            "select count(*) from entity where class_id=? and name like ?",
            (CLS_UNIT, pat)).fetchone()[0]
        if len(rows) != n_expected:
            problems.append(pat + ": " + str(len(rows)) + " rows vs "
                            + str(n_expected) + " units")
        for nm, v, t in rows:
            if t != "float":
                problems.append(nm + ": type=" + str(t))
            if abs(float(bytes(v).decode()) - val) > 1e-12:
                problems.append(nm + ": value=" + bytes(v).decode())

    dup = c.execute(
        "select count(*) from (select parameter_definition_id,entity_id,alternative_id "
        "from parameter_value group by 1,2,3 having count(*)>1)").fetchone()[0]
    if dup:
        problems.append(str(dup) + " duplicate parameter_value keys")

    if problems:
        print("\n*** SELF-CHECK FAILED ***")
        for p in problems:
            print("   - " + p)
        return 1

    print("guard OK " + str(g_after))
    print("self-checks OK (row count / type / value / duplicates)")
    print("integrity: " + c.execute("pragma integrity_check").fetchone()[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
