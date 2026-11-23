import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for fam in ("nuclear-3","CCGT+CC","CCGT","OCGT","wind-on-SP277-HH100","solar-PV-no-tracking"):
    r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='unit_investment_cost' AND e.name LIKE ? LIMIT 1""",(fam+"_%",)).fetchone()
    if not r: print("%-24s NO COST ROW"%fam); continue
    try:
        d=json.loads(bytes(r[0]).decode()); d=d.get("data",d)
        print("%-24s %s"%(fam[:24],{k[:4]:round(v,1) for k,v in d.items()}))
    except Exception:
        print("%-24s %s"%(fam[:24],r[0]))
