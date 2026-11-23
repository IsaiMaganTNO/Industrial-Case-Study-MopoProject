"""Discriminating test: force 1.0 unit of solar-PV-no-tracking_NLC5 to be built in 2050.

Baseline solve builds EXACTLY zero solar everywhere. If the LP is behaving correctly,
forcing a unit of the cheapest-LCOE technology must RAISE the objective (it is a binding
restriction on an optimal solution). If the objective instead FALLS or stays flat, the
baseline solution was not optimal w.r.t. solar -> structural defect (bad availability
linkage, missing unit__to_node flow, broken capacity_per_unit, etc.).

Writes investment_count_fix_new as a time_series on the Base alternative:
    2030 -> 0.0, 2040 -> 0.0, 2050 -> 1.0, 2060 -> null
Idempotent: copies the source DB only if the target does not already exist.
"""
import sqlite3, shutil, os, json

SRC = r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.sqlite"
DST = r"checkpoints\Final_SpineOpt_Model.tiny.3day.forcesolar.sqlite"
UNIT = "solar-PV-no-tracking_NLC5"
PARAM = "investment_count_fix_new"
ALT = "Base"

if not os.path.exists(DST):
    shutil.copyfile(SRC, DST)
    print("copied ->", DST)

con = sqlite3.connect(DST)
cur = con.cursor()

eid, ecls = cur.execute("select id,class_id from entity where name=?", (UNIT,)).fetchone()
pdid = cur.execute("select id from parameter_definition where name=? and entity_class_id=?", (PARAM, ecls)).fetchone()[0]
aid = cur.execute("select id from alternative where name=?", (ALT,)).fetchone()[0]
print("entity", eid, "class", ecls, "param_def", pdid, "alt", aid)

val = json.dumps({"type": "time_series", "data": {
    "2030-01-01T00:00:00": 0.0,
    "2040-01-01T00:00:00": 0.0,
    "2050-01-01T00:00:00": 1.0,
    "2060-01-01T00:00:00": None}}).encode()

row = cur.execute("select id from parameter_value where entity_id=? and parameter_definition_id=? and alternative_id=?", (eid, pdid, aid)).fetchone()
if row:
    cur.execute("update parameter_value set value=?, type=? where id=?", (val, "time_series", row[0]))
    print("updated existing row", row[0])
else:
    cols = [c[1] for c in cur.execute("pragma table_info(parameter_value)")]
    print("pv columns:", cols)
    data = {"entity_id": eid, "entity_class_id": ecls, "parameter_definition_id": pdid,
            "alternative_id": aid, "value": val, "type": "time_series"}
    data = {k: v for k, v in data.items() if k in cols}
    keys = ",".join(data)
    qs = ",".join("?" * len(data))
    cur.execute(f"insert into parameter_value ({keys}) values ({qs})", tuple(data.values()))
    print("inserted new row, keys:", keys)
con.commit()

chk = cur.execute("""select cast(pv.value as text) from parameter_value pv
join parameter_definition pd on pd.id=pv.parameter_definition_id
where pv.entity_id=? and pd.name=?""", (eid, PARAM)).fetchall()
print("verify:", chk)
con.close()
print("DONE")
