import sqlite3,collections
Q="""select c.name,e.name,pd.name,al.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id join alternative al on al.id=pv.alternative_id"""
def load(p): d=sqlite3.connect(p); return d,{r[:4]:r[4] for r in d.execute(Q)}
A,a=load(r"runs\3day_nb_ctry\input\Final_SpineOpt_Model.tiny.3day.nb_ctry.sqlite"); B,b=load(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ctry_ccslow.sqlite")
ch=[k for k in a if k in b and a[k]!=b[k]]
print("params",len(a),len(b),"added",len(b.keys()-a.keys()),"removed",len(a.keys()-b.keys()),"changed",len(ch),collections.Counter(k[2] for k in ch))
print("entities identical",set(A.execute("select class_id,name from entity"))==set(B.execute("select class_id,name from entity")))
sa=lambda d:set(d.execute("select s.name,sa.rank,a.name from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id"))
print("scenario diff",sa(A)^sa(B))
co2=[k for k in a if k[2]=="connection_flow_cost" and "_CO2_" in k[1].split("__")[0]]
print("CO2 connection_flow_cost rows in source",len(co2),"changed",sum(k in ch for k in co2))
# same new values as the IC1 pessimistic model for the same connections
C=sqlite3.connect(r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
ic={(r[1].split("__")[0],r[2]):r[4] for r in C.execute(Q) if r[2] in("connection_flow_cost","vom_cost")}
mm=[k for k in ch if ic.get((k[1].split("__")[0],k[2]))!=b[k]]
print("new values identical to IC1 pessimistic model:",len(ch)-len(mm),"/",len(ch))
