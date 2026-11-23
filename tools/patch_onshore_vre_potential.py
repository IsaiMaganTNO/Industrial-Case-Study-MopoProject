r"""Apply the pipeline-intended onshore VRE potential reduction (0.15) for IC1.

WHY
---
`scenario_config.yml!renewable_potentials` ships the intended values:
    include_onshore_potential_limitations: False   <-- never applied for IC1
    onshore_potentials: 0.15                       <-- the intended fraction
`onshore_potentials()` (scenario_run.py L321, CALLED at L734) multiplies
`investment_count_total_max_cumulative` on wind-on_* / solar-PV_* investment
groups by 0.15, floored at `max_capacity_history[tech][polygon]`.

It has NEVER run for IC1. Verified empirically: all 34 region-tech caps match the
source potential_*.xlsx at ratio 1.0000, i.e. no 0.15 reduction is present.

WHY A PATCH AND NOT THE FLAG
----------------------------
The function CANNOT be enabled as-is. `max_capacity_history` is keyed per COUNTRY
(wind-on BE 3.6 / NL 7.2; solar-PV BE 11.6 / NL 33.5) but the code looks the key up
per POLYGON (`BEC1`, `NLC3`, ...) via `entity_byname[0].split("_")[1]`. On IC1 names
this raises KeyError. If the floor were instead applied with the national number per
region it would make every region's floor the whole national history, which does not
reduce the caps at all - it RAISES them:

    literal national-floor-per-region     pro-rata national floor (this patch)
    wind-on  BE  21.27 ->  28.80 GW       21.27 ->   3.60 GW
    wind-on  NL  27.72 ->  64.80 GW       27.72 ->   7.20 GW
    solar-PV BE  85.10 ->  92.80 GW       85.10 ->  12.77 GW
    solar-PV NL 110.92 -> 301.50 GW      110.92 ->  33.50 GW

So the literal reading is self-evidently not the intent (a "reduction" that
multiplies NL solar headroom by 2.7x). This patch implements the INTENT:
  new_cap[r] = max(0.15 * cap[r],  hist_country * cap[r] / cap_country)
i.e. the national historical capacity is disaggregated PRO RATA by each region's
share of national potential, then used as a floor. Country totals then land on
exactly max(0.15 * national_potential, national_history).

RESULT (country totals, GW)
---------------------------
    wind-on  BE  21.27 ->   3.60      (history floor binds)
    wind-on  NL  27.72 ->   7.20      (history floor binds)
    solar-PV BE  85.10 ->  12.77      (0.15 binds)
    solar-PV NL 110.92 ->  33.50      (history floor binds)

CAVEAT
------
0.15 is an uncalibrated Europe-wide default; it was not derived for IC1. The
pro-rata floor is an INTERPRETATION of intent, not a documented rule - the data
authors should confirm it and ideally supply per-IC1-region historical capacities.
This stacks on top of the gas cap, so two constraints bind at once; if penalties
become non-zero the result is not interpretable.

SAFETY
------
- Operates on a COPY; SRC and DST are positional. --dry-run writes nothing.
- Idempotent: updates in place, never duplicates.
- type written as "float" on every row (NULL type can be SILENTLY DROPPED).
- Touches ONLY investment_group rows named wind-on_* / solar-PV_*. No electricity
  or cross-border component is modified; the cross-border guard
  (investment_count_initial_cumulative on class `connection`, 327 rows,
  sum 1522.5048) is asserted unchanged.
"""
import sqlite3, shutil, sys, os

PD_NAME = "investment_count_total_max_cumulative"
CLS_CONN = 1
ALT_BASE = 1
GUARD_ROWS, GUARD_SUM = 327, 1522.5048   # 17-region baseline; checked only with --expect-guard
FRACTION = 0.15
# Source: Pan-European-Framework.../_planning-input-processsing/scenario_config.yml
#         renewable_potentials.max_capacity_history (GW). NO absent there -> no floor (0.15 only).
HIST = {"wind-on": {"BE": 3.6, "NL": 7.2, "DE": 65.5, "DK": 5.2, "UK": 17.5, "FR": 24.8, "LU": 0.2},
        "solar-PV": {"BE": 11.6, "NL": 33.5, "DE": 107.9, "DK": 5.7, "UK": 20.2, "FR": 26.7, "LU": 0.6}}
# Region -> country: IC1 regions 'BEC1'/'NLC3' and country regions 'DE' both map via [:2].


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
        print("usage: patch_onshore_vre_potential.py SRC DST [--dry-run]")
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

    g_before = guard(c)
    print("cross-border guard before: " + str(g_before))
    if "--expect-guard" in sys.argv and (
            g_before[0] != GUARD_ROWS or abs(g_before[1] - GUARD_SUM) > 1e-6):
        print("UNEXPECTED BASELINE GUARD " + str(g_before) + " - ABORT")
        return 1

    pd_id, cls_ig = c.execute(
        "select pd.id, pd.entity_class_id from parameter_definition pd "
        "join entity_class ec on ec.id=pd.entity_class_id "
        "where pd.name=? and ec.name='investment_group'", (PD_NAME,)).fetchone()

    rows = list(c.execute(
        "select pv.id, e.name, pv.value from parameter_value pv "
        "join entity e on e.id=pv.entity_id "
        "where pv.parameter_definition_id=? and pv.alternative_id=? "
        "and (e.name like 'wind-on!_%' escape '!' "
        "     or e.name like 'solar-PV!_%' escape '!') order by e.name",
        (pd_id, ALT_BASE)))
    print("onshore groups found: " + str(len(rows)) + " (17-region baseline had 34)")
    if not rows:
        print("no onshore groups - ABORT")
        return 1

    cur = {}
    for rid, nm, v in rows:
        tech, reg = nm.rsplit("_", 1)
        cur[nm] = (rid, tech, reg, reg[:2], float(bytes(v).decode()))

    natl = {}
    for nm, (_, tech, _, ctry, val) in cur.items():
        natl[(tech, ctry)] = natl.get((tech, ctry), 0.0) + val

    plan = {}
    for nm, (rid, tech, reg, ctry, val) in cur.items():
        share = val / natl[(tech, ctry)] if natl[(tech, ctry)] else 0.0
        floor = HIST.get(tech, {}).get(ctry, 0.0) * share
        # never RAISE a cap: if history exceeds potential, keep the potential
        plan[nm] = (rid, val, min(val, max(val * FRACTION, floor)))

    for (tech, ctry) in sorted(natl):
        before = natl[(tech, ctry)]
        after = sum(p[2] for nm, p in plan.items()
                    if cur[nm][1] == tech and cur[nm][3] == ctry)
        if abs(after - before * FRACTION) < 1e-6:
            which = "0.15"
        elif abs(after - before) < 1e-6:
            which = "potential (history >= potential)"
        else:
            which = "history floor"
        print("  " + tech + " " + ctry + ": " + format(before, "8.2f")
              + " -> " + format(after, "7.2f") + " GW   (" + which + " binds)")

    if dry:
        print("\nDRY RUN - nothing written. " + str(len(plan)) + " rows would change.")
        return 0

    for nm, (rid, old, new) in plan.items():
        c.execute("update parameter_value set value=?, type=? where id=?",
                  (sqlite3.Binary(repr(float(new)).encode()), "float", rid))
    c.commit()
    print("\nupdated " + str(len(plan)) + " rows")

    problems = []
    g_after = guard(c)
    if g_after != g_before:
        problems.append("cross-border guard changed")

    for nm, (rid, old, new) in plan.items():
        v, t = c.execute("select value, type from parameter_value where id=?",
                         (rid,)).fetchone()
        if t != "float":
            problems.append(nm + ": type=" + str(t))
        if abs(float(bytes(v).decode()) - new) > 1e-9:
            problems.append(nm + ": value mismatch")
        if new > old + 1e-9:
            problems.append(nm + ": cap INCREASED " + str(old) + " -> " + str(new))

    # offshore must be untouched: only ids in `plan` were updated, all onshore by construction
    off_ids = {r[0] for r in c.execute(
        "select pv.id from parameter_value pv join entity e on e.id=pv.entity_id "
        "where pv.parameter_definition_id=? and e.name like 'wind-off%'", (pd_id,))}
    if off_ids & {p[0] for p in plan.values()}:
        problems.append("offshore groups were in the update set")

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
    print("self-checks OK (type / value / no-increase / offshore untouched / dups)")
    print("integrity: " + c.execute("pragma integrity_check").fetchone()[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
