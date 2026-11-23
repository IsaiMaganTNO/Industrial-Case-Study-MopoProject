import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for nd in ("global-H2","fossil-CH4","global-elec"):
    r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE e.name=? AND pd.name='tax_out_unit_flow'""",(nd,)).fetchone()
    if not r: print("%-12s (no tax row)"%nd); continue
    d=json.loads(bytes(r[0]).decode()); d=d.get("data",d)
    print("%-12s tax_out_unit_flow: %s"%(nd,d))
