"""Patch: book CO2 on HC combustion for units that burn HC but carry NO
emission accounting at all.

Background
----------
The model books CO2 in two consistent tiers:
  * carrier fuels, upstream at supply:  fossil-CH4 0.200 (LNG-terminal,
    gas-extraction), coal 0.350, waste 0.300, crude 0.260
  * industry process routes, at the unit, keyed on the unit's OWN OUTPUT:
    66 families, e.g. REF-SMR 0.019, REF-SMR-MEA 0.002, CEM2-(BMW)MEA -0.308

HC falls through BOTH tiers.  No HC supply node carries a CO2_content booking
the way fossil-CH4 does, and power/heat units get no process-route factor.
Five families therefore burn HC entirely carbon-free:

    oil-eng (17), oil-eng-existing (3), oil-boiler-existing (17),
    (LN+EL)O (7), printing-and-media-production-reference (17)   = 61 units

Consequence: HC is priced ~10x cleaner per MWh than CH4, and the model builds
5.484 units of NEW oil-eng in 2050 running 43 TWh in a net-zero system.

What this patch does
--------------------
Adds, for each of the 61 target units:
    unit__to_node          <unit>__atmosphere
    unit_flow__unit_flow   <unit>__atmosphere__HC_<reg>__<unit>
    flow_ratio_equality_coefficient = 0.24     (HC CO2_content, ton/MWh,
                                                data/Commodities/commodity_data.csv)

Keyed on the HC INPUT flow, mirroring exactly how SCPC-existing books coal
(SCPC-existing_BEC4__atmosphere__coal__SCPC-existing_BEC4 = 0.35).

Deliberately NOT touched
------------------------
Units that already carry an atmosphere flow are skipped, so no unit can end up
with both a fuel-based and a route-based booking.  In particular (LN)O and
(LN)O-MEA already carry route factors (0.967 / 0.111) on their olefins output
and are left alone -- patching them would double-count.

Known limitation: (LN+EL)O is an olefins route, so its HC is partly FEEDSTOCK
(carbon embodied in product) rather than combusted.  Charging it at 0.24
overstates its emissions.  It is included because it currently pays ZERO, which
is further from the truth; flagged for the route-based fix.
"""
import sqlite3, shutil, os, sys, collections

SRC = r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
DST = r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite"
# Positional override so the patch can be applied to any model build:
#   python tools\patch_hc_co2.py [SRC DST] [--dry-run]
_pos = [a for a in sys.argv[1:] if not a.startswith("--")]
if len(_pos) >= 2:
    SRC, DST = _pos[0], _pos[1]
HC_CO2 = 0.24
DRY = "--dry-run" in sys.argv

if not DRY and not os.path.exists(DST):
    shutil.copyfile(SRC, DST)
    print("copied ->", DST)

con = sqlite3.connect(SRC if DRY else DST)
cur = con.cursor()

CLS = {name: eid for eid, name in cur.execute("select id,name from entity_class").fetchall()}
cid_u2n  = CLS["unit__to_node"]
cid_ff   = CLS["unit_flow__unit_flow"]
cid_n2u  = CLS["node__to_unit"]
pd_id    = cur.execute("select id from parameter_definition where name='flow_ratio_equality_coefficient' and entity_class_id=?", (cid_ff,)).fetchone()[0]
alt_base = cur.execute("select id from alternative where name='Base'").fetchone()[0]
atm_id   = cur.execute("select id from entity where name='atmosphere'").fetchone()[0]

have_atm = set(n.replace("__atmosphere", "") for (n,) in cur.execute(
    "select e.name from entity e where e.class_id=? and e.name like '%__atmosphere'", (cid_u2n,)))

targets = []
for eid, name in cur.execute(
        "select id,name from entity where class_id=? and name like 'HC\\_%' escape '\\'", (cid_n2u,)):
    node, unit = name.split("__", 1)
    if unit in have_atm:
        continue
    targets.append((unit, node, name, eid))

print("target units:", len(targets))
for k, v in sorted(collections.Counter(u.rsplit("_", 1)[0] for u, _, _, _ in targets).items()):
    print(f"   {k:48s} {v}")
if DRY:
    print("DRY RUN - nothing written"); con.close(); sys.exit(0)

def next_id():
    return cur.execute("select coalesce(max(id),0)+1 from entity").fetchone()[0]

added_u2n = added_ff = added_pv = 0
for unit, node, n2u_name, n2u_id in targets:
    uid = cur.execute("select id from entity where class_id=? and name=?", (CLS["unit"], unit)).fetchone()[0]
    # 1. unit__to_node  <unit>__atmosphere
    u2n_name = f"{unit}__atmosphere"
    row = cur.execute("select id from entity where class_id=? and name=?", (cid_u2n, u2n_name)).fetchone()
    if row:
        u2n_id = row[0]
    else:
        u2n_id = next_id()
        cur.execute("insert into entity (id,class_id,name) values (?,?,?)", (u2n_id, cid_u2n, u2n_name))
        cur.execute("insert into entity_element (entity_id,entity_class_id,element_id,dimension_id,position) values (?,?,?,?,?)",
                    (u2n_id, cid_u2n, uid, CLS["unit"], 0))
        cur.execute("insert into entity_element (entity_id,entity_class_id,element_id,dimension_id,position) values (?,?,?,?,?)",
                    (u2n_id, cid_u2n, atm_id, CLS["node"], 1))
        added_u2n += 1
    # 2. unit_flow__unit_flow  <u2n>__<n2u>
    ff_name = f"{u2n_name}__{n2u_name}"
    row = cur.execute("select id from entity where class_id=? and name=?", (cid_ff, ff_name)).fetchone()
    if row:
        ff_id = row[0]
    else:
        ff_id = next_id()
        cur.execute("insert into entity (id,class_id,name) values (?,?,?)", (ff_id, cid_ff, ff_name))
        cur.execute("insert into entity_element (entity_id,entity_class_id,element_id,dimension_id,position) values (?,?,?,?,?)",
                    (ff_id, cid_ff, u2n_id, CLS["unit_flow"], 0))
        cur.execute("insert into entity_element (entity_id,entity_class_id,element_id,dimension_id,position) values (?,?,?,?,?)",
                    (ff_id, cid_ff, n2u_id, CLS["unit_flow"], 1))
        added_ff += 1
    # 3. the coefficient  -- value MUST be BLOB
    row = cur.execute("select id from parameter_value where parameter_definition_id=? and entity_id=?", (pd_id, ff_id)).fetchone()
    if not row:
        cur.execute("insert into parameter_value (parameter_definition_id,entity_id,entity_class_id,type,value,alternative_id)"
                    " values (?,?,?,?,?,?)",
                    (pd_id, ff_id, cid_ff, "float", sqlite3.Binary(repr(HC_CO2).encode()), alt_base))
        added_pv += 1

con.commit()
print(f"added unit__to_node={added_u2n} unit_flow__unit_flow={added_ff} parameter_value={added_pv}")
con.close()
print("DONE")
