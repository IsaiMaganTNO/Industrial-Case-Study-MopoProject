import sqlite3, json
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
q="""SELECT e.name, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='availability_factor' AND e.name LIKE 'wind-on-SP277%' LIMIT 1"""
n,v=c.execute(q).fetchone()
v=v.decode() if isinstance(v,bytes) else v
d=json.loads(v)
print(n); print("keys:",list(d.keys()))
print("index:",json.dumps(d.get("index"))[:200])
dat=d["data"]; print("data type:",type(dat).__name__,"len",len(dat))
print("first5:",dat[:5] if isinstance(dat,list) else list(dat.items())[:5])
