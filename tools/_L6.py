import sqlite3, json, collections
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
q="""SELECT e.name, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='availability_factor' AND pv.alternative_id=
       (SELECT id FROM alternative WHERE name='wy2008')"""
DAYS=("-05-14","-09-10","-12-24")
agg=collections.defaultdict(lambda:[0.0,0,0.0,0])
for n,v in c.execute(q):
    v=v.decode() if isinstance(v,bytes) else v
    tech=n.rsplit("_",1)[0]
    if not any(k in tech for k in ("wind-on-SP277","wind-off-FB-SP370","solar-PV-no-tracking")): continue
    d=json.loads(v)["data"]
    items=d.items() if isinstance(d,dict) else [(p[0],p[1]) for p in d]
    a=agg[tech]
    for k,x in items:
        x=float(x); a[0]+=x; a[1]+=1
        if any(dd in str(k) for dd in DAYS): a[2]+=x; a[3]+=1
print(f"{'tech':30s}{'annual CF':>11s}{'3-day CF':>11s}{'ratio':>9s}")
for t,a in sorted(agg.items()):
    if a[3]==0: print(f"{t:30s} no day match"); continue
    ann=a[0]/a[1]; three=a[2]/a[3]
    print(f"{t:30s}{ann:11.4f}{three:11.4f}{three/ann:9.2f}")
