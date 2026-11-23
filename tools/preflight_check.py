r"""Pre-flight checks for the coarsened tiny model. Run BEFORE every solve.

WHY THIS EXISTS
---------------
Every expensive failure in this project so far has been SILENT: the model
solved to OPTIMAL and produced plausible numbers that were answers to the wrong
question. Each check below corresponds to a failure that actually happened.

  1. OPERATIONS RESOLUTION must be 365D.
     If make_tiny_model.py did not run, the blocks are still 1h and the build
     explodes to 8760 timesteps per year. Caught by build time, eventually -
     but only after wasting it.

  2. REPRESENTATIVE WEIGHTS must sum to exactly 1.0.
     representative_blocks_by_period is a CONVEX combination. If it sums to
     365 instead, SpineOpt rejects it outright; if it sums to something else,
     operational costs are silently scaled by that factor. The sum being
     exactly 1.0 is also what makes the /365 CO2 patch valid for ANY number of
     representative days, which is why it is checked rather than assumed.

  3. ATMOSPHERE CO2 CAPS must be rescaled.
     Without the /365 patch the cumulative budget is drawn down once per year
     instead of 365 times, so the cap is 365x too loose and never binds. It
     fails silently because `atmosphere` carries balance_penalty = 10000.0.
     See docs/TIME_REPRESENTATION.md section 7.

  4. REPRESENTATIVE PERIOD DATES must be the days you intended.
     THIS IS THE ONE THAT COST 6h42m. clustering_output.py derived block_start
     from a stale representative_periods.csv, so a run pinned to
     (12 Jan, 19 Aug) was actually built on (12 Jan, 18 FEB). It solved to
     OPTIMAL as a two-WINTER-day model. Every other check above passed.
     Nothing downstream can detect this - the dates must be eyeballed against
     intent, which is why they are PRINTED and not merely validated.

USAGE
-----
    .\.venv\Scripts\python.exe tools\preflight_check.py
    .\.venv\Scripts\python.exe tools\preflight_check.py --db <path> --expect-days 12 231

Exits non-zero if any check fails, so it can gate a solve script.
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys

from spinedb_api import DatabaseMapping, from_database

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(REPO, "checkpoints", "Final_SpineOpt_Model.tiny.sqlite")

WANT_RESOLUTION = "365D"
CAP_PATCHED_BELOW = 1.0
WEIGHT_TOLERANCE = 1e-9


def _fmt(ok):
    return "PASS" if ok else "FAIL"


def main() -> None:
    ap = argparse.ArgumentParser(description="Pre-flight checks for the tiny model.")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--expect-days", type=int, nargs="+", default=None,
                    help="day-of-year values you INTENDED to run, e.g. 12 231")
    ap.add_argument("--cap-below", type=float, default=None,
                    help="threshold for 'CO2 cap rescaled'. Default 1.0 suits the "
                         "BE+NL budget (165.4/365=0.45). The six-country mixed run "
                         "needs ~10 (1146.35/365=3.14; unpatched would be 1146).")
    a = ap.parse_args()
    global CAP_PATCHED_BELOW
    if a.cap_below is not None:
        CAP_PATCHED_BELOW = a.cap_below

    if not os.path.isfile(a.db):
        sys.exit("not found: %s" % a.db)

    url = "sqlite:///" + os.path.abspath(a.db).replace("\\", "/")
    failures = []
    print("pre-flight: %s" % a.db)
    print("")

    with DatabaseMapping(url) as db:
        pvs = list(db.get_parameter_value_items())

        # ---- 1. operations resolution ---------------------------------
        print("[1] operations resolution (want %s)" % WANT_RESOLUTION)
        found = False
        for pv in pvs:
            if pv["parameter_definition_name"] == "resolution" and \
                    "operations" in str(pv["entity_byname"]):
                found = True
                val = str(from_database(pv["value"], pv["type"]))
                ok = val == WANT_RESOLUTION
                if not ok:
                    failures.append("resolution %s = %s" % (pv["entity_byname"][0], val))
                print("    %-22s %-8s %s" % (pv["entity_byname"][0], val, _fmt(ok)))
        if not found:
            failures.append("no operations_y* resolution found")
            print("    none found                     FAIL")

        # ---- 2. representative weights sum to 1 -----------------------
        print("")
        print("[2] representative_blocks_by_period (want sum = 1.0)")
        found = False
        for pv in pvs:
            if pv["parameter_definition_name"] != "representative_blocks_by_period":
                continue
            found = True
            m = from_database(pv["value"], pv["type"])
            vec = list(m.values)[0]
            vals = [float(x) for x in vec.values]
            total = sum(vals)
            ok = abs(total - 1.0) < WEIGHT_TOLERANCE
            if not ok:
                failures.append("%s weights sum to %.6f" % (pv["entity_byname"][0], total))
            print("    %-22s entries=%-4d sum=%.6f nonzero=%s %s"
                  % (pv["entity_byname"][0], len(m.indexes), total,
                     [round(x, 5) for x in vals if x != 0], _fmt(ok)))
        if not found:
            failures.append("no representative_blocks_by_period found")
            print("    none found                     FAIL")

        # ---- 3. atmosphere CO2 caps patched ---------------------------
        print("")
        print("[3] atmosphere CO2 caps (want rescaled by 1/365)")
        found = False
        for pv in pvs:
            if pv["entity_byname"] != ("atmosphere",) or \
                    "cumulative" not in pv["parameter_definition_name"]:
                continue
            found = True
            v = from_database(pv["value"], pv["type"])
            try:
                vals = [float(x) for x in v.values]
            except AttributeError:
                vals = [float(v)]
            ok = max(vals) < CAP_PATCHED_BELOW
            if not ok:
                failures.append("%s not rescaled (max %.2f)"
                                % (pv["parameter_definition_name"], max(vals)))
            print("    %-46s %s %s"
                  % (pv["parameter_definition_name"],
                     [round(x, 8) for x in vals], _fmt(ok)))
        if not found:
            failures.append("no atmosphere cumulative caps found")
            print("    none found                     FAIL")

        # ---- 4. representative period DATES ---------------------------
        print("")
        print("[4] representative period dates  <-- CHECK THESE AGAINST INTENT")
        rows = {}
        for pv in pvs:
            n = pv["parameter_definition_name"]
            bn = pv["entity_byname"]
            if n in ("block_start", "representative_block_index", "weight") and \
                    "representative_period" in str(bn):
                rows.setdefault(bn[0], {})[n] = from_database(pv["value"], pv["type"])
        if not rows:
            failures.append("no representative_period temporal blocks found")
            print("    none found                     FAIL")
        days_seen = []
        for e in sorted(rows):
            r = rows[e]
            start = str(r.get("block_start"))
            doy = None
            try:
                d = datetime.datetime.fromisoformat(start)
                doy = d.timetuple().tm_yday
                pretty = d.strftime("%d %b %Y")
            except Exception:
                pretty = start
            days_seen.append(doy)
            print("    %-30s %s  (day %s)  idx=%s  weight=%.2f"
                  % (e, pretty, doy, r.get("representative_block_index"),
                     float(r.get("weight", 0))))

        # Indexes must be contiguous from 1: a gap means block_start was built
        # from a stale representative_periods.csv and SpineOpt will refuse the
        # build with "no representative temporal block(s) with indexes ...".
        idxs = sorted(int(r["representative_block_index"]) for r in rows.values()
                      if "representative_block_index" in r)
        if idxs and idxs != list(range(1, len(idxs) + 1)):
            failures.append("representative_block_index not contiguous: %s" % idxs)
            print("    indexes %s  NOT CONTIGUOUS  FAIL" % idxs)

        if a.expect_days:
            uniq = sorted(set(d for d in days_seen if d is not None))
            want = sorted(set(a.expect_days))
            ok = uniq == want
            if not ok:
                failures.append("days are %s but you expected %s" % (uniq, want))
            print("")
            print("    expected days %s, found %s  %s" % (want, uniq, _fmt(ok)))

    print("")
    if failures:
        print("PRE-FLIGHT FAILED (%d):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        sys.exit(1)
    print("all checks PASSED")
    if not a.expect_days:
        print("NOTE: run with --expect-days to assert the dates in [4] "
              "instead of eyeballing them.")


if __name__ == "__main__":
    main()
