import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def last(v):
    try:
        d=json.loads(bytes(v).decode()); d=d.get("data",d)
        return list(d.values())[-1] if isinstance(d,dict) else d
    except Exception:
        try: return float(v)
        except Exception: return str(v)[:20]
for pat in ("PEM_NLC1__","SMR+CC_NLC1__"):
    print("=== %s ==="%pat)
    for n,v in c.execute("""SELECT e.name,pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ?""",(pat+"%",)):
        print("   %-54s %s"%(n[:54],last(v)))
