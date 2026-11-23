import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("temporal blocks:")
for n, in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='temporal_block'"):
    eid=c.execute("select id from entity where name=?",(n,)).fetchone()[0]
    ps={p:bytes(v).decode() for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
        join parameter_definition pd on pd.id=pv.parameter_definition_id where pv.entity_id=?""",(eid,))}
    print(f"  {n:22s} start={ps.get('block_start','')[:40]:42s} end={ps.get('block_end','')[:30]}")
    if 'weight' in ps: print(f"      weight={ps['weight'][:60]}")
