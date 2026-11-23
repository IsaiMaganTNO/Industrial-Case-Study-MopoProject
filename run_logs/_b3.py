import sqlite3, pandas as pd
pd.set_option("display.width",95)
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
q="""SELECT e.name ent, pd.name param,
 CASE WHEN typeof(pv.value)='blob' THEN CAST(pv.value AS TEXT) ELSE pv.value END val
 FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 WHERE e.name LIKE 'oil-eng%NLC1%' OR e.name LIKE 'CCGT%NLC1%'
 ORDER BY e.name,pd.name"""
df=pd.read_sql(q,c)
df["val"]=df.val.astype(str).str.slice(0,70)
print(df.to_string())
