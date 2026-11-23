import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for fam in ("(NG)PE","(LN)O","BF-BOF"):
    print("=== %s ==="%fam)
    for n,v in c.execute("""SELECT e.name,pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ? AND e.name LIKE '%atmosphere%'
      LIMIT 3""",(fam+"_%",)):
        try: d=list(json.loads(bytes(v).decode())["data"].values())[-1]
        except Exception: d=bytes(v)[:12]
        print("   %-56s %s"%(n[:56],d))
