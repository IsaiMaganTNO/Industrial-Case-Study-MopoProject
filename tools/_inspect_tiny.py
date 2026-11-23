"""One-shot sanity inspection of the tiny model before solving. Read-only."""
import json
import sqlite3
import sys
from collections import defaultdict

DB = "checkpoints/Final_SpineOpt_Model.tiny.sqlite"
con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
con.execute("PRAGMA foreign_keys = OFF")


def num(raw):
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except Exception:
            return None
    try:
        v = json.loads(raw)
    except Exception:
        return None
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


print("=" * 70)
print("DB:", DB)

# --- 1. atmosphere emission factors, grouped by technology family -----------
rows = con.execute(
    """SELECT e.name, pv.value FROM parameter_value pv
       JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
       JOIN entity e ON e.id=pv.entity_id
       WHERE pd.name='flow_ratio_equality_coefficient'
         AND e.name LIKE '%atmosphere%'"""
).fetchall()

fam = defaultdict(set)
for n, v in rows:
    f = num(v)
    if f is None:
        continue
    unit = n.split("__")[0]
    # strip trailing _<REGION><digits>
    base = unit.rsplit("_", 1)[0] if "_" in unit else unit
    fam[base].add(round(f, 6))

print("\n[1] atmosphere emission factors: %d rows, %d families" % (len(rows), len(fam)))
incons = {k: v for k, v in fam.items() if len(v) > 1}
print("    families with >1 distinct value (expect 0):", len(incons))
for k, v in sorted(incons.items())[:10]:
    print("      !! %-40s %s" % (k, sorted(v)))

print("\n    all families:")
for k in sorted(fam):
    vals = sorted(fam[k])
    print("      %-42s %s" % (k, vals[0] if len(vals) == 1 else vals))

# --- 2. CCS vs unabated twins ----------------------------------------------
print("\n[2] CCS vs unabated pairs")
for base in sorted(fam):
    for tag in ("MEA", "CaL", "CCS", "OXY"):
        if tag in base:
            plain = base.replace("-" + tag, "").replace(tag, "").strip("-_")
            for cand in fam:
                if cand == plain and cand != base:
                    a, b = sorted(fam[cand])[0], sorted(fam[base])[0]
                    verdict = "OK" if b < a else "!! NOT LOWER"
                    print("      %-28s %8s   ->  %-28s %8s   %s" % (cand, a, base, b, verdict))

# --- 3. negatives -----------------------------------------------------------
neg = [(n, num(v)) for n, v in rows if (num(v) or 0) < 0]
print("\n[3] negative (BECCS) factors: %d" % len(neg))
for n, v in sorted(neg):
    print("      %-50s %s" % (n.split("__")[0], v))

# --- 4. magnitude sanity ----------------------------------------------------
vals = [num(v) for _, v in rows if num(v) is not None]
big = [v for v in vals if abs(v) > 5]
tiny = [v for v in vals if 0 < abs(v) < 1e-6]
print("\n[4] magnitudes: min=%.6g max=%.6g" % (min(vals), max(vals)))
print("    |v|>5 (suspicious): %d    0<|v|<1e-6 (scaling risk): %d" % (len(big), len(tiny)))

# --- 5. temporal ------------------------------------------------------------
print("\n[5] temporal blocks")
for pname in ("resolution", "representative_periods_mapping"):
    for n, v in con.execute(
        """SELECT e.name, pv.value FROM parameter_value pv
           JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
           JOIN entity e ON e.id=pv.entity_id WHERE pd.name=?""",
        (pname,),
    ).fetchall():
        s = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        print("      %-22s %-28s %s" % (pname, n, s[:60]))

# --- 6. counts --------------------------------------------------------------
print("\n[6] entity counts by class (top 15)")
for cls, cnt in con.execute(
    """SELECT ec.name, COUNT(*) c FROM entity e
       JOIN entity_class ec ON ec.id=e.class_id
       GROUP BY ec.name ORDER BY c DESC LIMIT 15"""
):
    print("      %-40s %6d" % (cls, cnt))

print("\n[7] totals")
for lbl, q in (
    ("entities", "SELECT COUNT(*) FROM entity"),
    ("parameter_values", "SELECT COUNT(*) FROM parameter_value"),
    ("alternatives", "SELECT COUNT(*) FROM alternative"),
    ("scenarios", "SELECT COUNT(*) FROM scenario"),
):
    print("      %-20s %8d" % (lbl, con.execute(q).fetchone()[0]))

print("\n    scenarios:", [r[0] for r in con.execute("SELECT name FROM scenario")])
con.close()
print("=" * 70)
