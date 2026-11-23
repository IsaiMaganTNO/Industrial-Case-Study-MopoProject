import sqlite3, pandas as pd
pd.set_option("display.width",95)
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
print("== entity table cols =="); print([r[1] for r in c.execute("PRAGMA table_info(entity)")])
print("== entity_element cols =="); print([r[1] for r in c.execute("PRAGMA table_info(entity_element)")])
print("== entity_class cols =="); print([r[1] for r in c.execute("PRAGMA table_info(entity_class)")])
print("== parameter_value cols =="); print([r[1] for r in c.execute("PRAGMA table_info(parameter_value)")])
print()
for cls in ("unit__to_node","unit_flow__unit_flow"):
    r=c.execute("select id,name,dimension_id_list from entity_class where name=?",(cls,)).fetchone()
    print(cls, "-> id",r[0],"dims",r[2])
