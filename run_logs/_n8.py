import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def g(pat,par):
    r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name=? AND e.name LIKE ? LIMIT 1""",(par,pat+"_%")).fetchone()
    if not r: return None
    try:
        d=json.loads(bytes(r[0]).decode()); d=d.get("data",d)
        return list(d.values())[2] if isinstance(d,dict) else float(d)
    except Exception:
        try: return float(bytes(r[0]).decode())
        except Exception:
            try: return float(r[0])
            except Exception: return None
print("%-22s %10s %10s %8s"%("tech 2050","capex","fom","life"))
for f in ("nuclear-3","CCGT+CC","CCGT","OCGT","wind-on-SP277-HH100","solar-PV-no-tracking"):
    cap=g(f,"unit_investment_cost"); fom=g(f,"fom_cost")
    r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='lifetime_technical' AND e.name LIKE ? LIMIT 1""",(f+"_%",)).fetchone()
    lt=bytes(r[0]).decode().strip('"') if r else "-"
    print("%-22s %10s %10s %8s"%(f[:22],("%.1f"%cap) if cap else "-",("%.5f"%fom) if fom else "-",lt))
