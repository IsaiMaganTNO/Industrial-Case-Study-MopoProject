"""Patch: disable cross-border electricity trade with non-NL/BE zones.

Sets investment_count_initial_cumulative = 0, investment_count_max_cumulative = 0
and investment_count_fix_new = 0 on all 19 cross-border ELECTRICITY connections.
Idempotent. Only touches connections whose name is <A>_elec_<B> where A or B is a
foreign zone (UK/DE/FR/NO/DK/LU). Domestic NL/BE interconnectors are untouched,
as are all non-electricity (H2, CH4, bio, CO2) cross-border links.
"""
import sqlite3, shutil, sys, os, json

SRC = r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.sqlite"
DST = r"checkpoints\Final_SpineOpt_Model.tiny.3day.noxborder.sqlite"
EXT = ("UK","DE","FR","NO","DK","LU")

if not os.path.exists(DST):
    shutil.copyfile(SRC, DST)
    print("copied ->", DST)

con = sqlite3.connect(DST)
cur = con.cursor()

conns = []
for (n,) in cur.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=:c",{"c":"connection"}):
    if "_elec_" not in n: continue
    a,b = n.split("_elec_",1)
    if a in EXT or b in EXT: conns.append(n)
conns.sort()
print("target connections:", len(conns))

PARAMS = ("investment_count_initial_cumulative",
          "investment_count_max_cumulative",
          "investment_count_fix_new")
qm = ",".join("?"*len(conns))
rows = cur.execute(
    "select pv.id, e.name, pd.name, pv.type from parameter_value pv "
    "join entity e on e.id=pv.entity_id "
    "join parameter_definition pd on pd.id=pv.parameter_definition_id "
    f"where e.name in ({qm}) and pd.name in (?,?,?)",
    tuple(conns)+PARAMS).fetchall()
print("parameter_value rows to zero:", len(rows))

ZERO = b"0.0"
n=0
for pvid, ent, pname, ptype in rows:
    cur.execute("update parameter_value set value=?, type=? where id=?", (ZERO, "float", pvid))
    n+=1
con.commit()
print("rows updated:", n)

# verify
bad=0
for pvid, ent, pname, _ in rows:
    v = cur.execute("select value from parameter_value where id=?", (pvid,)).fetchone()[0]
    if isinstance(v,bytes): v=v.decode()
    if float(v)!=0.0: bad+=1
print("verify non-zero remaining:", bad)
con.close()
print("DONE")
