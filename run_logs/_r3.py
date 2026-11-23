import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def last(v):
    try:
        d=json.loads(bytes(v).decode()); d=d.get("data",d)
        return list(d.values())[-1] if isinstance(d,dict) else d
    except Exception:
        try: return float(v)
        except Exception: return str(v)[:16]
print("%-18s %14s %12s"%("unit","investcost","initial_cum"))
for fam in ("CCGT","CCGT+CC","CCGT-existing","CEM2-(Afm)","CEM2-(Afm)MEA","BF-BOF","BF-BOF-MEA","REF-SMR","REF-SMR-MEA"):
    r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='unit_investment_cost' AND e.name LIKE ? LIMIT 1""",(fam+"_%",)).fetchone()
    r2=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='investment_count_initial_cumulative' AND e.name LIKE ? LIMIT 1""",(fam+"_%",)).fetchone()
    print("%-18s %14s %12s"%(fam,last(r[0]) if r else "-",last(r2[0]) if r2 else "-"))
