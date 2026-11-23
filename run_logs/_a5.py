import sqlite3, pandas as pd
pd.set_option("display.width",95); pd.set_option("display.max_rows",200)
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
q="""SELECT e.name ent, ec.name cls, pd.name param,
 CASE WHEN typeof(pv.value)='blob' THEN CAST(pv.value AS TEXT) ELSE pv.value END val
 FROM parameter_value pv
 JOIN entity e ON e.id=pv.entity_id
 JOIN entity_class ec ON ec.id=e.class_id
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 WHERE e.name IN ('battery-storage_NLC1__elec_NLC1','battery-storage_NLC1',
   'battery-storage-iron-air_NLC1','PEM_NLC1','SMR_NLC1')
 ORDER BY e.name, pd.name"""
print(pd.read_sql(q,c).to_string())
