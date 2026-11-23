"""Raise low_CO2 CO2-storage-NSNL012 cap in 2050 (and 2060 tail) to 10.0 Mt/yr -> total 12.5 Mt/yr with NSNL031 2.5.
usage: python tools/patch_co2cap2050.py SRC DST"""
import sqlite3, shutil, os, sys, json
SRC, DST = sys.argv[1], sys.argv[2]
assert not os.path.exists(DST), "DST exists"
shutil.copyfile(SRC, DST)
c = sqlite3.connect(DST)
rows = c.execute("""select pv.id, cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id
 join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id
 where e.name='CO2-storage-NSNL012' and pd.name='storage_investment_count_fix_cumulative' and a.name='low_CO2'""").fetchall()
assert len(rows) == 1, rows
pid, txt = rows[0]; d = json.loads(txt)
for k in ("2050-01-01T00:00:00", "2060-01-01T00:00:00"):
    assert abs(d["data"][k] * 365 - 8.0) < 1e-9, d["data"][k]
    d["data"][k] = 10.0 / 365
c.execute("update parameter_value set value=? where id=?", (sqlite3.Binary(json.dumps(d).encode()), pid))
c.commit(); print("new:", {k[:4]: round(v * 365, 3) for k, v in d["data"].items()})
