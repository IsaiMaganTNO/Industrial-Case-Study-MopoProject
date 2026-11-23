import sqlite3, json, statistics as st
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
# exact block starts
blocks=[]
for n, in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='temporal_block' and e.name like 'representative_period_2050%'"):
    eid=c.execute("select id from entity where name=?",(n,)).fetchone()[0]
    d={p:bytes(v).decode() for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
       join parameter_definition pd on pd.id=pv.parameter_definition_id where pv.entity_id=?""",(eid,))}
    s=json.loads(d["block_start"])["data"]; e=json.loads(d["block_end"])["data"]
    w=float(d["weight"]); blocks.append((n,s,e,w))
    print(f"{n}: {s} -> {e}  weight={w:.2f}")
import datetime as dt
print()
for u in ["solar-PV-no-tracking_NLC3","wind-on-SP277-HH100_NLC3"]:
    v=c.execute("""select pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id
      where e.name=? and pd.name='availability_factor' and al.name='wy2008'""",(u,)).fetchone()[0]
    d=json.loads(bytes(v).decode()); vals=[float(x) for x in d["data"]]
    ann=st.mean(vals)
    tot=0.0; wsum=0.0
    for n,s,e,w in blocks:
        sd=dt.datetime.fromisoformat(s); ed=dt.datetime.fromisoformat(e)
        h0=(sd-dt.datetime(sd.year,1,1)).days*24+sd.hour
        h1=(ed-dt.datetime(sd.year,1,1)).days*24+ed.hour
        seg=vals[h0:h1]
        tot+=st.mean(seg)*w; wsum+=w
        print(f"   {u[:26]:26s} {n[-1]} hours {h0:5d}-{h1:5d} CF={st.mean(seg):.4f} w={w:.1f}")
    print(f"   {u[:26]:26s} ANNUAL CF={ann:.4f}   SAMPLED weighted CF={tot/wsum:.4f}   bias={(tot/wsum)/ann-1:+.1%}\n")
