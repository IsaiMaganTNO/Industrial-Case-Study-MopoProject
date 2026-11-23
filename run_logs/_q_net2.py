import sqlite3,re,json
d=sqlite3.connect(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
def P(e,p):
  r=d.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name=? and pd.name=?",(e,p)).fetchone()
  return None if r is None else json.loads(r[0])
def mx(v): return max(v["data"].values()) if isinstance(v,dict) else v
Z=re.compile(r"^((BE|NL)C\d+)_(elec|H2)_((BE|NL)C\d+)$")
for car in ["elec","H2"]:
  cs=[r[0] for r in d.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='connection'") if Z.match(r[0]) and Z.match(r[0]).group(3)==car]
  exp=[c for c in cs if mx(P(c,"investment_count_max_cumulative"))>float(P(c,"investment_count_initial_cumulative"))+1e-9]
  nocost=[c for c in cs if P(c,"connection_investment_cost") is None]
  print(car,len(cs),"expandable",len(exp),"no-cost",len(nocost),"expandable&no-cost",len(set(exp)&set(nocost)))
cav=[r[0] for r in d.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='connection' and e.name like '%salt-cavern%'")]
print("cavern conns",len(cav),"with inv cost",sum(P(c,"connection_investment_cost") is not None for c in cav),"with flow cost",
 d.execute("select count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name like '%salt-cavern%' and pd.name like '%flow_cost%'").fetchone()[0])
print("salt-cavern NLC2 inv cost series:",P("salt-cavern_NLC2","storage_investment_cost"))
