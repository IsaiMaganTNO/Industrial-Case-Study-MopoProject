import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def last(v):
    try:
        d=json.loads(bytes(v).decode()); d=d.get("data",d)
        return list(d.values())[2] if isinstance(d,dict) and len(d)>2 else d
    except Exception:
        try: return float(bytes(v).decode())
        except Exception:
            try: return float(v)
            except Exception: return None
print("2050 unit_investment_cost by cement route (BEC7 vs NLC5):")
for fam in ("CEM2-(Afm)","CEM2-(Afm)MEA","LC3-(Afm)Oxy-MEA","CEM2-(Afm)CaL"):
    for reg in ("BEC7","NLC5"):
        r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          WHERE pd.name='unit_investment_cost' AND e.name=?""",(fam+"_"+reg,)).fetchone()
        print("   %-18s %-6s %s"%(fam[:18],reg,last(r[0]) if r else "-"))
