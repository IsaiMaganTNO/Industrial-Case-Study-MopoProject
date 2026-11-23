"""Divide the `atmosphere` CO2 budget by 365.

The cap is stored as `storage_investment_count_max_cumulative` on the
`atmosphere` node; the effective budget is cap x `storage_state_max` (=1000).
SpineOpt debits the long-term storage once per representative block, while
flows are annualised by representative-day weights summing to 365. The stored
cap must therefore be pre-divided by 365.

Verified empirically from Investment_Results.3day_hcco2.sqlite:
  node_state_longterm(atmosphere) 2030 = 453.1507 -> x365 = 165,400 (headline)

Scope: the `atmosphere` node ONLY. Cross-border electricity connections are
untouched and guarded.
"""
import argparse, shutil, sqlite3, json, sys

DIV = 365.0
GUARD_XBORDER = 26.060

def xborder_sum(con):
    """Sum of initial investment counts on connection entities.

    NOTE: the parameter is `investment_count_initial_cumulative` on the
    `connection` entity class. An earlier version of this guard used a
    non-existent name and silently returned 0.0, making it vacuous.
    """
    rows = con.execute("""
        SELECT cast(pv.value as text) FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
        JOIN entity e ON e.id=pv.entity_id
        JOIN entity_class ec ON ec.id=e.class_id
        WHERE pd.name='investment_count_initial_cumulative'
          AND ec.name='connection'""").fetchall()
    assert rows, "cross-border guard found 0 rows - parameter name wrong"
    t = 0.0
    for (v,) in rows:
        try: t += float(v)
        except Exception: pass
    return t

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.dry_run:
        shutil.copyfile(a.src, a.dst)
    target = a.src if a.dry_run else a.dst
    con = sqlite3.connect(target)

    before_xb = xborder_sum(con)

    row = con.execute("""
        SELECT pv.id, cast(pv.value as text), typeof(pv.value)
        FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
        JOIN entity e ON e.id=pv.entity_id
        WHERE e.name='atmosphere'
          AND pd.name='storage_investment_count_max_cumulative'""").fetchall()
    assert len(row) == 1, "expected exactly 1 atmosphere cap row, got %d" % len(row)
    pid, txt, typ = row[0]
    assert typ == "blob", "cap value is %s, expected blob" % typ

    obj = json.loads(txt)
    data = obj["data"]
    assert isinstance(data, dict), "unexpected cap payload type %s" % type(data)

    print("%-24s %16s %16s" % ("timestamp", "before", "after"))
    newdata = {}
    for k, v in data.items():
        f = float(v)
        if f > 10.0:
            nf = f / DIV
        elif f == 0.0:
            nf = 0.0
        else:
            sys.exit("ABORT: %s = %r already looks divided; refusing." % (k, f))
        newdata[k] = nf
        print("%-24s %16.4f %16.10f" % (k[:24], f, nf))
    obj["data"] = newdata

    blob = sqlite3.Binary(json.dumps(obj).encode("utf-8"))
    if a.dry_run:
        print("\nDRY RUN - nothing written.")
        return
    con.execute("UPDATE parameter_value SET value=? WHERE id=?", (blob, pid))
    con.commit()
    fix_initial(con)

    chk = con.execute("""
        SELECT typeof(pv.value), cast(pv.value as text) FROM parameter_value pv
        WHERE pv.id=?""", (pid,)).fetchone()
    assert chk[0] == "blob", "post-write type is %s" % chk[0]
    rt = json.loads(chk[1])["data"]
    # Readback against what we computed (was hard-coded to the BE+NL budget
    # 165.4/36.8, which no longer holds for the six-country mixed run).
    for k, nf in newdata.items():
        assert abs(float(rt[k]) - nf) < 1e-12, (k, rt[k], nf)

    after_xb = xborder_sum(con)
    assert abs(after_xb - before_xb) < 1e-9, "cross-border changed!"
    print("\nGUARD cross-border initial sum: %.3f (unchanged)" % after_xb)
    print("GUARD cap row type: blob, readback OK")
    con.close()
    print("WROTE %s" % a.dst)


def fix_initial(con):
    """Also divide the scalar `storage_investment_count_initial_cumulative`.

    Added 2026-10-09: this script originally divided ONLY the max_cumulative
    series. The 17-region chain got the initial value divided upstream by the
    older patch_co2_caps.py (0.4531 = 165.4/365); a fresh build does not, and
    preflight_check flagged initial = 1146.35. Values <= 10 are treated as
    already divided and left alone (idempotent).
    """
    rows = con.execute("""
        SELECT pv.id, cast(pv.value as text), pv.type FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
        JOIN entity e ON e.id=pv.entity_id
        WHERE e.name='atmosphere'
          AND pd.name='storage_investment_count_initial_cumulative'""").fetchall()
    for pid, txt, typ in rows:
        f = float(txt)
        if f > 10.0:
            nf = f / DIV
            con.execute("UPDATE parameter_value SET value=?, type='float' WHERE id=?",
                        (sqlite3.Binary(repr(nf).encode()), pid))
            print("initial_cumulative: %.4f -> %.10f" % (f, nf))
        else:
            print("initial_cumulative: %.10f already divided - left as is" % f)
    con.commit()

main()
