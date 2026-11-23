import pickle,re,sqlite3,pandas as pd
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
db=sqlite3.connect(r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
atm=set(x[0] for x in db.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit__to_node' and e.name like '%__atmosphere'"))
atmfam={re.sub(r"_(BE|NL)C\d+__atmosphere$","",a) for a in atm}
for k in ["IC1","MR"]:
  U=pd.Series(r[k]["U"]).rename("v").reset_index(); U.columns=["y","c","car","dr","fam","v"]; U=U[(U.y==2050)&U.c.isin(["NL","BE"])]
  for car in ["CH4","HC"]:
    x=U[(U.car==car)&(U.dr=="from_node")].groupby("fam").v.sum()/1e3; x=x[x>0.3]
    print(k,car,"consumers TWh [has atmosphere row?]:",{f:(round(v,1),f in atmfam) for f,v in x.items()})
  C=pd.Series(r[k]["C"]).rename("v").reset_index(); C.columns=["y","cn","node","dr","v"]; C=C[(C.y==2050)&C.cn.str.contains("_HC_")]
  print(k,"HC connection flow TWh:",round(C[C.dr=="to_node"].v.sum()/1e3,1))
print("HC demand nodes:",[x for x in db.execute("select e.name from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='demand' and e.name like 'HC%' limit 3")])
print("hcco2 patch (oil-eng atm rows):",sum(1 for a in atm if a.startswith("oil-eng")))
