import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite"
c=sqlite3.connect(db)
print("entity_alternative cols:",[r[1] for r in c.execute("pragma table_info(entity_alternative)")])
for tag,nm in [("FWD","BEC3_CO2_BEC6"),("REV","BEC6_CO2_BEC3"),
               ("CH4f","BEC1_CH4_BEC2"),("CH4r","BEC2_CH4_BEC1")]:
    r=c.execute("select id from entity where name=?",(nm,)).fetchone()
    if not r: print(tag,nm,"MISSING"); continue
    eid=r[0]
    ea=c.execute("select alternative_id,active from entity_alternative where entity_id=?",(eid,)).fetchall()
    print(f"{tag:5s} {nm:16s} eid={eid:6d} entity_alternative={ea}")
print("\ntotal entity_alternative rows:",c.execute("select count(*) from entity_alternative").fetchone())
# how many CO2 conns have an entity_alternative row at all?
print("CO2 conns with EA row:",c.execute("""
 select count(*) from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='connection' and e.name like '%!_CO2!_%' escape '!'
 and exists(select 1 from entity_alternative ea where ea.entity_id=e.id)""").fetchone())
print("all conns with EA row:",c.execute("""
 select count(*) from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='connection' and exists(select 1 from entity_alternative ea where ea.entity_id=e.id)""").fetchone())
