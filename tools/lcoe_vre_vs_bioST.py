import sqlite3, json, collections, datetime as dt, statistics as st
DB=r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite"
c=sqlite3.connect(DB)
def pv(e,p,alt=1):
    q="""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         WHERE e.name=? AND pd.name=? AND pv.alternative_id=?"""
    r=c.execute(q,(e,p,alt)).fetchone()
    if not r: return None
    v=r[0].decode() if isinstance(r[0],bytes) else r[0]
    try:
        d=json.loads(v)
        if isinstance(d,dict) and "data" in d:
            dd=d["data"]; return float(list(dd.values())[0]) if isinstance(dd,dict) else float(dd)
        return float(d)
    except Exception: return None

# availability: rep-day vs annual, per unit family
REP=[(5,14),(9,10),(12,24)]
q="""SELECT e.name, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='availability_factor' AND pv.alternative_id=19"""
rep=collections.defaultdict(list); ann=collections.defaultdict(list)
for n,v in c.execute(q):
    v=v.decode() if isinstance(v,bytes) else v
    d=json.loads(v); idx=d.get("index",{}); data=d.get("data")
    vals=list(data.values()) if isinstance(data,dict) else data
    start=dt.datetime.fromisoformat(idx.get("start","2018-01-01 00:00:00"))
    t=n.rsplit('_',1)[0]
    for i,x in enumerate(vals):
        ts=start+dt.timedelta(hours=i); ann[t].append(float(x))
        if (ts.month,ts.day) in REP: rep[t].append(float(x))

CASES=[("bioST_BEC1",None),("wind-on-SP277-HH100_BEC1","wind-on-SP277-HH100_BEC1"),
       ("wind-off-FB-SP370-HH155_NSNL011","wind-off-FB-SP370-HH155_NSNL011"),
       ("solar-PV-no-tracking_BEC1","solar-PV-no-tracking_BEC1")]
r_ = 0.05; LIFE=25
crf = r_*(1+r_)**LIFE/((1+r_)**LIFE-1)
print(f"{'technology':32s}{'capex':>9s}{'CF_rep':>8s}{'CF_ann':>8s}{'LCOE_rep':>10s}{'LCOE_ann':>10s}")
for u,availkey in CASES:
    cap=pv(u,"unit_investment_cost"); fom=pv(u,"fom_cost") or 0.0
    if availkey:
        t=availkey.rsplit('_',1)[0]
        cf_r=st.mean(rep[t]) if rep.get(t) else None
        cf_a=st.mean(ann[t]) if ann.get(t) else None
    else:
        cf_r=cf_a=0.85   # dispatchable biomass steam, assumed high availability
    if not cap or not cf_r: continue
    lc_r=(cap*crf+fom*8760)/(cf_r*8760)
    lc_a=(cap*crf+fom*8760)/(cf_a*8760)
    print(f"{u[:32]:32s}{cap:9.0f}{cf_r:8.3f}{cf_a:8.3f}{lc_r:10.2f}{lc_a:10.2f}")
