import sqlite3
b=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite")
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
old={r[0] for r in b.execute("select id from entity")}
new={r[0] for r in c.execute("select id from entity")}
mine=new-old
print("entities created:",len(mine),"(expect 140 = 35*4)")
print("min/max new id:",min(mine),max(mine))
q="select count(*) from entity_element el join entity e on e.id=el.element_id where el.entity_id in (%s) and e.class_id<>el.dimension_id"%",".join(map(str,mine))
print("MY rows violating class/dimension rule:",c.execute(q).fetchone()[0])
q2="select count(*) from entity_element where entity_id in (%s)"%",".join(map(str,mine))
print("MY entity_element rows total:",c.execute(q2).fetchone()[0],"(expect 245 = 35*7)")
# and parameter values
q3="select count(*) from parameter_value where entity_id in (%s)"%",".join(map(str,mine))
print("MY parameter_value rows:",c.execute(q3).fetchone()[0],"(expect 70 = 35*2)")
print("\nbaseline FK violations:",len(b.execute("pragma foreign_key_check").fetchall()))
print("patched  FK violations:",len(c.execute("pragma foreign_key_check").fetchall()))
