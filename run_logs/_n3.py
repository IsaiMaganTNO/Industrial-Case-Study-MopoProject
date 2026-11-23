import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def last(v):
    try:
        d=json.loads(bytes(v).decode()); d=d.get("data",d)
        return d if isinstance(d,dict) else d
    except Exception:
        try: return float(v)
        except Exception: return str(v)[:30]
for n,p,v in c.execute("""SELECT e.name,pd.name,pv.value FROM parameter_value pv
  JOIN entity e ON e.id=pv.entity_id JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE e.name LIKE 'nuclear-3\\_%' ESCAPE '\\' AND pd.name IN
  ('unit_investment_cost','investment_count_max_cumulative','fom_cost','lifetime_technical')
  LIMIT 8"""):
    print("%-22s %-32s %s"%(n[:22],p[:32],str(last(v))[:40]))
