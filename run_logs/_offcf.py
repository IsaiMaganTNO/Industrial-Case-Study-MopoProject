import sqlite3, json, statistics as st, datetime as dt
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
blocks=[]
for n, in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"temporal_block\" and e.name like \"representative_period_2050%\""):
    eid=c.execute("select id from entity where name=?",(n,)).fetchone()[0]
    d={p:bytes(v).decode() for p,v in c.execute("select pd.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pv.entity_id=?",(eid,))}
    blocks.append((n,json.loads(d["block_start"])["data"],json.loads(d["block_end"])["data"],float(d["weight"])))
for u in ["wind-off-FO-SP370-HH155_NSNL031","wind-off-FB-SP370-HH155_NSNL031",
          "wind-on-SP277-HH100_NLC3","solar-PV-no-tracking_NLC3"]:
    r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id "
      "join entity e on e.id=pv.entity_id where e.name=? and pd.name=\"availability_factor\"",(u,)).fetchone()
    if not r: print(u,"no availability_factor"); continue
    vals=[float(x) for x in json.loads(bytes(r[0]).decode())["data"]]
    ann=st.mean(vals); tot=0.0; w=0.0; parts=[]
    for n,s,e,ww in blocks:
        sd=dt.datetime.fromisoformat(s); ed=dt.datetime.fromisoformat(e)
        h0=(sd-dt.datetime(sd.year,1,1)).days*24+sd.hour
        h1=(ed-dt.datetime(sd.year,1,1)).days*24+ed.hour
        m=st.mean(vals[h0:h1]); parts.append(f"{m:.4f}(w{ww:.0f})"); tot+=m*ww; w+=ww
    print(f"{u:34s} ann={ann:.4f} sampled={tot/w:.4f} bias={(tot/w)/ann-1:+.1%}  "+" ".join(parts))
