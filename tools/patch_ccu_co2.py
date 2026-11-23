"""Patch: close the CCU carbon leak for methanation.
CH4 carbon is booked only at the gateway (LNG / gas-extraction, 0.2 t/MWh), so
synthetic CH4 from methanation was burned carbon-free while its CO2 left the
CO2_* node -> captured CO2 counted as permanently removed.
Adds for each methanation_<reg>:  <unit>__atmosphere  and
unit_flow__unit_flow <unit>__atmosphere__<unit>__CH4_<reg> = 0.2 (keyed on CH4 output).
FT/MeOH routes are NOT patched: HC is booked at combustion (hcco2 patch) and MeOH
feeds only route-accounted olefins -> patching would double count.
usage: python tools/patch_ccu_co2.py SRC DST
"""
import sqlite3, shutil, os, sys
SRC, DST = sys.argv[1], sys.argv[2]
COEF = 0.2
assert not os.path.exists(DST), "DST exists"
shutil.copyfile(SRC, DST)
con = sqlite3.connect(DST); cur = con.cursor()
CLS = {n: i for i, n in cur.execute("select id,name from entity_class")}
u2n, ff = CLS["unit__to_node"], CLS["unit_flow__unit_flow"]
pd = cur.execute("select id from parameter_definition where name='flow_ratio_equality_coefficient' and entity_class_id=?", (ff,)).fetchone()[0]
alt = cur.execute("select id from alternative where name='Base'").fetchone()[0]
atm = cur.execute("select id from entity where name='atmosphere' and class_id=?", (CLS["node"],)).fetchone()[0]
units = cur.execute("select id,name from entity where class_id=? and name like 'methanation\\_%' escape '\\'", (CLS["unit"],)).fetchall()
assert len(units) in (17, 21, 23), len(units)  # 17 = NL+BE zones; 21 = mixed-res (+DE/DK/NO/UK); 23 = +FR/LU
nid = lambda: cur.execute("select coalesce(max(id),0)+1 from entity").fetchone()[0]
def add(cid, name, e0, d0, e1, d1):
    i = nid()
    cur.execute("insert into entity (id,class_id,name) values (?,?,?)", (i, cid, name))
    for p, (e, d) in enumerate([(e0, d0), (e1, d1)]):
        cur.execute("insert into entity_element (entity_id,entity_class_id,element_id,dimension_id,position) values (?,?,?,?,?)", (i, cid, e, d, p))
    return i
for uid, u in units:
    assert cur.execute("select count(*) from entity where class_id=? and name=?", (u2n, u + "__atmosphere")).fetchone()[0] == 0, u
    # CH4 output link: <unit>__CH4_<zone> (IC1) or <unit>__CH4_<country> (country-level)
    ch4 = cur.execute("select id,name from entity where class_id=? and substr(name,1,?)=?", (u2n, len(u) + 6, u + "__CH4_")).fetchall()
    assert len(ch4) == 1, (u, ch4)
    a = add(u2n, u + "__atmosphere", uid, CLS["unit"], atm, CLS["node"])
    f = add(ff, f"{u}__atmosphere__{ch4[0][1]}", a, CLS["unit_flow"], ch4[0][0], CLS["unit_flow"])
    cur.execute("insert into parameter_value (parameter_definition_id,entity_id,entity_class_id,type,value,alternative_id) values (?,?,?,?,?,?)",
                (pd, f, ff, "float", sqlite3.Binary(repr(COEF).encode()), alt))
con.commit(); print("patched", len(units), "methanation units"); con.close()

