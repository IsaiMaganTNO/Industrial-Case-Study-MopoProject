import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for nm in ["BEC3_CO2_BEC6__CO2_BEC3","BEC3_CO2_BEC6__CO2_BEC6","BEC3_CO2_BEC6__CO2_BEC6__CO2_BEC3"]:
    eid,cid=c.execute("select id,class_id from entity where name=?",(nm,)).fetchone()
    print(f"{nm}  eid={eid} class_id={cid}")
    for r in c.execute("select entity_id,entity_class_id,element_id,dimension_id,position from entity_element where entity_id=?",(eid,)):
        en=c.execute("select name from entity where id=?",(r[2],)).fetchone()[0]
        print("   ",r," -> ",en)
print("\nparameter_definition ids:")
for n in ["connection_flow_cost","fix_ratio_out_in_connection_flow"]:
    print("  ",n,c.execute("select id,entity_class_id from parameter_definition where name=?",(n,)).fetchall())
print("\nalternative Base:",c.execute("select id,name from alternative where name='Base'").fetchall())
print("max commit_id used:",c.execute("select max(commit_id) from entity").fetchone())
