"""Track CO2 emission factors across pipeline stages.

Read-only. Snapshots every CO2-emission-like value in a DB (INES schema or
SpineOpt schema) and appends a summary to a JSON ledger, so a later stage can
be diffed against an earlier one. Catches values being silently dropped,
zeroed or sign-flipped (BECCS negatives) somewhere downstream.

Usage:
    python tools/track_co2.py <stage-label> <db.sqlite>
    python tools/track_co2.py --report
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "logs" / "co2_ledger.json"

INES_PARAMS = ("co2_emission",)
SPINEOPT_PARAMS = (
    "flow_ratio_equality_coefficient",
    "fix_ratio_out_in_unit_flow",
    "unit_flow_coefficient",
)


def _scalar(raw):
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError:
            return None
    try:
        v = json.loads(raw)
    except (ValueError, TypeError):
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def _elements(con, eid):
    names = []
    for (nm,) in con.execute(
        "SELECT el.name FROM entity_element ee JOIN entity el ON el.id = ee.element_id "
        "WHERE ee.entity_id = ? ORDER BY ee.position",
        (eid,),
    ):
        names.append(nm)
        for (sub,) in con.execute(
            "SELECT el.name FROM entity_element ee JOIN entity el ON el.id = ee.element_id "
            "WHERE ee.entity_id = (SELECT id FROM entity WHERE name = ?) ORDER BY ee.position",
            (nm,),
        ):
            names.append(sub)
    return names


def snapshot(db):
    con = sqlite3.connect("file:{}?mode=ro".format(db.as_posix()), uri=True)
    con.execute("PRAGMA foreign_keys = OFF")
    wanted = INES_PARAMS + SPINEOPT_PARAMS
    placeholders = ",".join("?" * len(wanted))
    rows = con.execute(
        """SELECT pd.name, e.id, e.name, pv.value
           FROM parameter_value pv
           JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
           JOIN entity e ON e.id = pv.entity_id
           WHERE pd.name IN ({})""".format(placeholders),
        wanted,
    ).fetchall()

    values = {}
    per_param = {}
    for pname, eid, ename, raw in rows:
        per_param[pname] = per_param.get(pname, 0) + 1
        f = _scalar(raw)
        if f is None:
            continue
        if pname in SPINEOPT_PARAMS:
            if "atmosphere" not in ename and "atmosphere" not in _elements(con, eid):
                continue
        values["{}|{}".format(pname, ename)] = f
    con.close()

    neg = {k: v for k, v in values.items() if v < 0}
    return {
        "db": str(db),
        "when": datetime.now().isoformat(timespec="seconds"),
        "rows_by_parameter": per_param,
        "tracked_values": len(values),
        "negative_count": len(neg),
        "negative_sum": round(sum(neg.values()), 6),
        "positive_sum": round(sum(v for v in values.values() if v > 0), 6),
        "zero_count": sum(1 for v in values.values() if v == 0),
        "negatives": dict(sorted(neg.items())),
        "values": values,
    }


def record(label, db):
    snap = snapshot(db)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    ledger[label] = snap
    LEDGER.write_text(json.dumps(ledger, indent=2))
    print("[{}] {}".format(label, db))
    print("  rows by parameter : {}".format(snap["rows_by_parameter"]))
    print("  tracked values    : {}".format(snap["tracked_values"]))
    print("  negative (BECCS)  : {}  sum={}".format(snap["negative_count"], snap["negative_sum"]))
    print("  zero-valued       : {}".format(snap["zero_count"]))
    for k, v in list(snap["negatives"].items())[:5]:
        print("      {} = {}".format(k, v))
    print("  -> {}".format(LEDGER))


def report():
    if not LEDGER.exists():
        print("No ledger yet.")
        return 1
    ledger = json.loads(LEDGER.read_text())
    labels = list(ledger)
    print("{:<28}{:>9}{:>6}{:>12}{:>7}".format("stage", "tracked", "neg", "negsum", "zeros"))
    for lb in labels:
        s = ledger[lb]
        print("{:<28}{:>9}{:>6}{:>12}{:>7}".format(
            lb, s["tracked_values"], s["negative_count"], s["negative_sum"], s["zero_count"]))
    rc = 0
    for prev, cur in zip(labels, labels[1:]):
        a, b = ledger[prev], ledger[cur]
        print("")
        print("{}  ->  {}".format(prev, cur))
        bad = False
        if b["negative_count"] < a["negative_count"]:
            print("  !! NEGATIVES LOST: {} -> {}".format(a["negative_count"], b["negative_count"]))
            for k in sorted(set(a["negatives"]) - set(b["negatives"]))[:10]:
                print("       {}: {} -> {}".format(k, a["negatives"][k], b["values"].get(k)))
            bad = True
        if b["tracked_values"] == 0 and a["tracked_values"] > 0:
            print("  !! ALL VALUES DISAPPEARED")
            bad = True
        if bad:
            rc = 1
        else:
            print("  ok")
    return rc


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--report":
        return report()
    if len(args) != 2:
        print(__doc__)
        return 2
    label, dbarg = args
    db = Path(dbarg)
    if not db.is_absolute():
        db = ROOT / db
    if not db.exists():
        print("DB not found: {}".format(db))
        return 2
    record(label, db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
