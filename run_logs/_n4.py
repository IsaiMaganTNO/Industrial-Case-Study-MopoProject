import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def vals(v):
    try:
        d=json.loads(bytes(v).decode()); d=d.get("data",d)
        return d
    except Exception: return None
print("%-22s %12s %12s %12s %10s"%("tech","2030","2040","2050","fom"))
for fam in ("nuclear-3","CCGT+CC","CCGT","OCGT","wind-on-SP277-HH100","solar-PV-no-tracking","wind-off-FB-SP370-HH15"):
    r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='unit_investment_cost' AND e.name LIKE ? LIMIT 1""",(fam+"\\_%",)).fetchone()
    r2=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='fom_cost' AND e.name LIKE ? LIMIT 1""",(fam+"\\_%",)).fetchone()
    d=vals(r[0]) if r else None
    fom=None
    if r2:
        try: fom=float(r2[0]) if not isinstance(r2[0],bytes) else float(bytes(r2[0]).decode())
        except Exception: fom=vals(r2[0])
    if d: print("%-22s %12.1f %12.1f %12.1f %10s"%(fam[:22],
        list(d.values())[0],list(d.values())[1],list(d.values())[2],("%.5f"%fom) if isinstance(fom,float) else fom))
