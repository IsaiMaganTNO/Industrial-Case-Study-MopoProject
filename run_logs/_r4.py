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
# are existing (brownfield) units ever CC-capable?
print("families with initial_cumulative>0 (existing fleet):")
seen={}
for n,v in c.execute("""SELECT e.name,pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE pd.name='investment_count_initial_cumulative'"""):
    import re
    f=re.sub(r'_(NL|BE)C\d+$','',n)
    try: val=float(last(v))
    except Exception: continue
    if val>0: seen[f]=seen.get(f,0)+val
for k,v in sorted(seen.items(),key=lambda z:-z[1])[:22]:
    cc = "CC" if ("CC" in k or "MEA" in k or "Oxy" in k or "CaL" in k) else ""
    print("   %-34s %10.3f %s"%(k[:34],v,cc))
