import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def last(v):
    try:
        d=json.loads(bytes(v).decode()); d=d.get("data",d)
        return list(d.values())[-1] if isinstance(d,dict) else d
    except Exception:
        try: return float(v)
        except Exception: return str(v)[:18]
for fam in ("PEM","SMR+CC","LH2-terminal","SMR"):
    print("=== %s ==="%fam)
    for pn in ("unit_investment_cost","fom_cost","investment_count_max_cumulative"):
        r=c.execute("""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          WHERE pd.name=? AND e.name LIKE ? LIMIT 1""",(pn,fam+"\_%".replace("\\",""))).fetchone()
        if r: print("   %-32s %s"%(pn,last(r[0])))
