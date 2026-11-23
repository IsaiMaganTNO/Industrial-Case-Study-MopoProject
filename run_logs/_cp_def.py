import sqlite3,re,os,collections
p=r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_cp.sqlite"
c=sqlite3.connect(p)
q="""select ec.name, pd.name, pd.default_value, pd.default_type from parameter_definition pd join entity_class ec on ec.id=pd.entity_class_id
where ec.name like 'connection%' order by ec.name, pd.name"""
for r in c.execute(q):
    v=r[2].decode() if isinstance(r[2],bytes) else r[2]
    if v not in (None,"null"): print(r[0],r[1],v[:60],r[3])
