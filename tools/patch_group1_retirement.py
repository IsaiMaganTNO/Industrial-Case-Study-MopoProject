"""Group 1 retirement test patch.

Converts `investment_count_max_cumulative` from a flat float scalar to a
declining time_series, using the shape proven by `solar-PV-existing_BEC1`:

    {2030: X, 2041: X/2, 2050: 0.0, 2060: 0.0}

where X is the unit's `investment_count_initial_cumulative` (its endowment),
matching the exemplar where initial == the 2030 cap value.

Scope: 26 units / 3 techs -- BF-BOF (2), (NG)PEA (12), (NG)PE (12).

EXCLUDED: Scraps_EAF_BEC3 (pvid 14228) and Scraps_EAF_BEC5 (pvid 14234).
These are the SOLE producers of `steel-secondary_BEC3` / `_BEC5`, which carry
a demand exactly equal to the endowment (0.1986972884931507 /
0.10838033917808218) with no alternative unit, no connection import route and
no balance_penalty. Forcing their capacity to zero is provably infeasible --
it caused the INFEASIBLE_OR_UNBOUNDED result on the 28-unit attempt.

Idempotent: guards on type="float", so re-running is a no-op.
"""
import sqlite3, json, sys

DB = sys.argv[1]

PVIDS = {
 12285:1.6159236529680365, 12291:0.001643835616438356, 12297:0.04851598173515982,
 12303:0.09557077625570776, 12309:0.19958904109589043, 12315:0.004955043150684931,
 12321:0.018420091324200912, 12327:0.09349315068493151, 12333:0.004955043150684931,
 12339:0.004955043150684931, 12345:1.5479186847031965, 12351:0.16310344497716894,
 12357:0.48607305936073064, 12363:0.0031963470319634705, 12369:0.10319634703196347,
 12375:0.01945205479452055, 12381:0.2826301369863014, 12387:0.004307376164383561,
 12393:0.02995433789954338, 12399:0.005384220205479452, 12405:0.005384220205479452,
 12411:0.06491618367579909, 12417:0.2380782841324201, 12423:0.14726027397260275,
 12499:0.6050228312785388, 12505:0.8044520547945205,
}
EXCLUDED = {14228, 14234}   # Scraps_EAF -- see module docstring

assert len(PVIDS) == 26, len(PVIDS)
assert not (set(PVIDS) & EXCLUDED)

c = sqlite3.connect(DB)
changed = skipped = 0
for pvid, X in PVIDS.items():
    row = c.execute("SELECT type, value FROM parameter_value WHERE id=?", (pvid,)).fetchone()
    if row is None:
        raise SystemExit(f"FATAL: pvid {pvid} not found")
    if row[0] != "float":
        skipped += 1
        continue
    blob = json.dumps({"data": {
        "2030-01-01T00:00:00": X,
        "2041-01-01T00:00:00": X / 2.0,
        "2050-01-01T00:00:00": 0.0,
        "2060-01-01T00:00:00": 0.0,
    }}).encode("utf-8")
    c.execute("UPDATE parameter_value SET type='time_series', value=? WHERE id=?", (blob, pvid))
    changed += 1
c.commit()
print(f"changed={changed} skipped(already time_series)={skipped}")

n = c.execute("SELECT COUNT(*) FROM parameter_value WHERE id IN (%s) AND type='time_series'"
              % ",".join(map(str, PVIDS))).fetchone()[0]
print(f"now time_series: {n} / 26")

for pvid in sorted(EXCLUDED):
    t, v = c.execute("SELECT type, value FROM parameter_value WHERE id=?", (pvid,)).fetchone()
    print(f"excluded pvid {pvid}: type={t} (must be float)")

