import sqlite3,collections,json
Q="""select c.name,e.name,pd.name,al.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id join alternative al on al.id=pv.alternative_id"""
def load(p): d=sqlite3.connect(p); return d,{r[:4]:r[4] for r in d.execute(Q)}
A,a=load(r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"); B,b=load(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_ccslow.sqlite")
ch=[k for k in a if k in b and a[k]!=b[k]]
print("params",len(a),len(b),"added",len(b.keys()-a.keys()),"removed",len(a.keys()-b.keys()),"changed",len(ch),collections.Counter(k[2] for k in ch))
print("entities identical",set(A.execute("select class_id,name from entity"))==set(B.execute("select class_id,name from entity")))
sa=lambda d:set(d.execute("select s.name,sa.rank,a.name from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id"))
print("scenario diff",sa(A)^sa(B))
co2=[k for k in a if k[2] in("connection_flow_cost","vom_cost") and ("_CO2_" in k[1].split("__")[0] or k[1].startswith("CO2-injection-"))]
print("CO2 cost rows in source",len(co2),"changed",sum(k in ch for k in co2))
# low_CO2 caps per site (max over years) vs high_CO2
def caps(alt):
  out={}
  for k,v in a.items():
    if k[3]==alt and k[2]=="storage_investment_count_fix_cumulative":
      x=json.loads(v); vals=[z for z in x["data"].values() if z is not None]; out[k[1].replace("CO2-storage-","")]=max(vals)
  return out
lo,hi=caps("low_CO2"),caps("high_CO2")
print("site cap (max, model units) low vs high:"); [print(f"   {s:10s} {lo[s]:.4f} {hi[s]:.4f}") for s in sorted(hi)]
