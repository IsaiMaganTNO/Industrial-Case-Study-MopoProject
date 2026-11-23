import sqlite3, pandas as pd
pd.set_option("display.width",95)
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
q="""SELECT ec.name cls, e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
 WHERE lower(e.name) LIKE '%batt%' OR lower(e.name) LIKE '%iron-air%'
    OR lower(e.name) LIKE '%electroly%' OR lower(e.name) LIKE '%pem%'
    OR lower(e.name) LIKE '%soec%' OR lower(e.name)LIKE '%aec%'"""
df=pd.read_sql(q,c)
print(df.cls.value_counts().to_string())
print()
print(df[df.cls=="unit"].to_string())
print()
print(df[df.cls=="node"].to_string())
