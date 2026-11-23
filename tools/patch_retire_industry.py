r"""Extend the Group 1 forced-retirement treatment to ALL feasible industrial
incumbents.

Applies the SAME shape the original 26-unit patch used (and the same shape the
pipeline itself uses for e.g. `solar-PV-existing_BEC1`):

    investment_count_max_cumulative = {2030: X, 2041: X/2, 2050: 0, 2060: 0}

where X = the unit's `investment_count_initial_cumulative` (its endowment).

SCOPE is decided by `tools/screen_retirement.py`, not by hand. A unit is
patched only if, in ITS OWN REGION, at least one other unit feeds the same
commodity node AND the others' combined capacity covers that node's demand.
That screen independently re-derives the two `Scraps_EAF` exclusions that
caused the historical INFEASIBLE_OR_UNBOUNDED, and additionally catches five
`Diaphragm` (chlorine) units that are sole producers in all five regions.

Two tiers are written, so a failure can be bisected without redoing analysis:

  TIER "priced"    24 units - incumbents that HAVE a `unit_investment_cost`.
                   Glass (NG)_gco/_gfl/_gfi, olefins (LN)O, ammonia (NG)NH3,
                   cement EU-mix-2018. These are real, priced plants competing
                   against real, priced alternatives.

  TIER "scaffold" 175 units - `*-production-reference` units that have NO
                   `unit_investment_cost` and NO `fom_cost`, and whose
                   `investment_count_max_cumulative` is a flat 1000.0 that they
                   rail to in the solution. These look like modelling
                   scaffolding rather than physical plant. Retiring them may be
                   the wrong fix (the right one may be upstream in the
                   pipeline) - they are included because they are the reason 6
                   of 12 charted sectors are flat, but they are tagged so the
                   run can be repeated without them.

BLOB SAFETY: SpineOpt stores `parameter_value.value` as a BLOB. Writing a
Python `str` crashes the Julia solve. We write bytes and assert the stored
type afterwards.

Idempotent: only rewrites rows whose current type is 'float'.

Usage:
  python tools\patch_retire_industry.py <db.sqlite> [--tier priced|scaffold|both]
"""
import sqlite3, json, csv, sys, collections, re, os

DB = sys.argv[1]
TIER = "both"
if "--tier" in sys.argv:
    TIER = sys.argv[sys.argv.index("--tier") + 1]
# The screen CSV must match the DB being patched.  It used to be hardcoded to
# run_logs/retire_screen.csv, which silently applied a STALE screen when a new
# model build (e.g. the 7-day rebuild) produced a different RETIRE-SAFE set.
SCREEN = os.path.join("run_logs", "retire_screen.csv")
if "--screen" in sys.argv:
    SCREEN = sys.argv[sys.argv.index("--screen") + 1]

rows = [r for r in csv.DictReader(open(SCREEN, encoding="utf8"))
        if r["verdict"] == "RETIRE-SAFE"]
if not rows:
    raise SystemExit("FATAL: screen produced no RETIRE-SAFE rows")
print(f"screen file: {SCREEN}")

con = sqlite3.connect(DB)
c = con.cursor()


def pvid_and_type(unit, par):
    c.execute("""select pv.id, pv.type, cast(pv.value as text)
     from parameter_value pv
     join parameter_definition pd on pd.id=pv.parameter_definition_id
     join entity e on e.id=pv.entity_id
     join entity_class ec on ec.id=pd.entity_class_id
     where pd.name=? and e.name=? and ec.name='unit'""", (par, unit))
    return c.fetchone()


priced, scaffold = [], []
for r in rows:
    (priced if pvid_and_type(r["unit"], "unit_investment_cost") else scaffold).append(r)
print(f"screen RETIRE-SAFE: {len(rows)}  priced={len(priced)} scaffold={len(scaffold)}")

targets = {"priced": priced, "scaffold": scaffold, "both": priced + scaffold}[TIER]
print(f"tier={TIER} -> patching {len(targets)} units")

# Guard: never touch a unit the screen did not clear.
cleared = {r["unit"] for r in rows}
assert all(t["unit"] in cleared for t in targets)

changed = skipped = 0
for t in targets:
    row = pvid_and_type(t["unit"], "investment_count_max_cumulative")
    if row is None:
        raise SystemExit(f"FATAL: no investment_count_max_cumulative for {t['unit']}")
    pvid, typ, _ = row
    if typ != "float":
        skipped += 1
        continue
    X = float(t["endowment"])
    blob = json.dumps({"data": {
        "2030-01-01T00:00:00": X,
        "2041-01-01T00:00:00": X / 2.0,
        "2050-01-01T00:00:00": 0.0,
        "2060-01-01T00:00:00": 0.0,
    }}).encode("utf-8")
    c.execute("UPDATE parameter_value SET type='time_series', value=? WHERE id=?",
              (sqlite3.Binary(blob), pvid))
    changed += 1
con.commit()
print(f"changed={changed} skipped(already time_series)={skipped}")

# ---- verification -------------------------------------------------------
bad = c.execute("""select count(*) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 where pd.name='investment_count_max_cumulative' and pv.type='time_series'
   and typeof(pv.value)!='blob'""").fetchone()[0]
print(f"non-blob time_series rows: {bad} (must be 0)")
assert bad == 0, "BLOB CORRUPTION - do not solve this DB"

for t in targets[:2]:
    _, typ, val = pvid_and_type(t["unit"], "investment_count_max_cumulative")
    print(f"  sample {t['unit']}: {typ} {val[:70]}")

# Blocked units must remain untouched floats.
for u in ("Scraps_EAF_BEC3", "Scraps_EAF_BEC5", "Diaphragm_BEC1"):
    r = pvid_and_type(u, "investment_count_max_cumulative")
    if r:
        print(f"  guard {u}: type={r[1]} (must be float)")
        assert r[1] == "float", f"{u} was patched but is BLOCKED"
