import sqlite3,json,pickle
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
eid=c.execute("select id from entity where name='biofuels'").fetchone()[0]
v=c.execute("""select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 where pv.entity_id=? and pd.name='investment_count_total_max_cumulative'""",(eid,)).fetchone()[0]
print("biofuels CAP:",json.loads(bytes(v).decode())["data"])
# members
mem=[r[0] for r in c.execute("""select e2.name from entity e
  join entity_class ec on ec.id=e.class_id
  join entity_element l0 on l0.entity_id=e.id and l0.position=0
  join entity e2 on e2.id=l0.element_id
  join entity_element l1 on l1.entity_id=e.id and l1.position=1
  join entity g on g.id=l1.element_id
  where ec.name='unit__investment_group' and g.name='biofuels'""")]
print(f"\nmembers ({len(mem)}):",mem[:10])
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
base=set(x.split('_')[0] for x in mem)
for tag,D in [("BASELINE",A),("BIDIR   ",D) if False else ("BIDIR   ",B)]:
    f=D["fleet"]
    sel=f[f["tech"].astype(str).isin(base)]
    print(f"{tag} biofuels-group fleet by year:",sel.groupby("year")["value"].sum().round(3).to_dict() if "value" in f.columns else list(f.columns))
