import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("=== Is gas-extraction a unit or a storage node? ===")
for n in ["gas-extraction_NLC3","CH4-geo-formation_NLC3"]:
    r=c.execute("select ec.name from entity e join entity_class ec on ec.id=e.class_id where e.name=?",(n,)).fetchall()
    print(f"  {n:28s} class(es): {[x[0] for x in r]}")
print()
print("=== gas-extraction topology (what feeds it, what it feeds) ===")
for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name in ('unit__to_node','node__to_unit') and e.name like '%gas-extraction_NLC3%'"):
    print("   ",n)
print()
print("=== CH4-geo-formation topology ===")
for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where e.name like '%CH4-geo-formation_NLC3%'"):
    cls=c.execute("select ec.name from entity e join entity_class ec on ec.id=e.class_id where e.name=?",(n,)).fetchone()[0]
    print(f"    [{cls}] {n}")
