import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
q="""SELECT e.name, pd.name, pv.value FROM parameter_value pv
JOIN entity e ON e.id=pv.entity_id
JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
WHERE e.name LIKE '%aluminium%'"""
for n,p,v in c.execute(q):
    try: s=json.loads(bytes(v).decode())
    except Exception: s=bytes(v)[:60]
    print("%-62s %-26s %s"%(n[:62],p[:26],str(s)[:60]))
