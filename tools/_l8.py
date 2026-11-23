import sqlite3, json, collections, datetime
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
START=datetime.datetime(2018,1,1)
DAYS=[datetime.date(2018,5,14),datetime.date(2018,9,10),datetime.date(2018,12,24)]
idx=set()
for d0 in DAYS:
    h0=int((datetime.datetime(d0.year,d0.month,d0.day)-START).total_seconds()//3600)
    idx.update(range(h0,h0+24))
q="""SELECT e.name, pv.alternative_id, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='availability_factor' AND pv.alternative_id=
       (SELECT id FROM alternative WHERE name='wy2008')"""
agg=collections.defaultdict(lambda:[0.0,0,0.0,0])
for n,a,v in c.execute(q):
    v=v.decode() if isinstance(v,bytes) else v
    tech=n.rsplit("_",1)[0]
    if not any(k in tech for k in ("wind-on-SP277","wind-off-FB-SP370","solar-PV-no-tracking")): continue
    dat=json.loads(v)["data"]
    g=agg[tech]
    for i,x in enumerate(dat):
        x=float(x); g[0]+=x; g[1]+=1
        if i in idx: g[2]+=x; g[3]+=1
print(f"{'tech':28s}{'annual CF':>11s}{'3-day CF':>11s}{'ratio':>8s}")
for t,g in sorted(agg.items()):
    ann=g[0]/g[1]; thr=g[2]/g[3]
    print(f"{t:28s}{ann:11.4f}{thr:11.4f}{thr/ann:8.2f}")
