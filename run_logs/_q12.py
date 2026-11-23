import pickle,re,sqlite3,pandas as pd
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
db=sqlite3.connect(r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
atm={x[0].split("__")[0] for x in db.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit__to_node' and e.name like '%__atmosphere'")}
U=pd.Series(r["IC1"]["U"]).rename("v").reset_index(); U.columns=["y","c","car","dr","fam","v"]; U=U[U.y==2050]
for car in ["HC","CH4","MeOH"]:
  x=U[(U.car.str.startswith(car))&(U.dr=="from_node")&(U.c=="?")].groupby("fam").v.sum()/1e3; x=x[x>0.5].sort_values(ascending=False)
  print(car,"consumers with unparsed region (TWh):",x.round(1).head(15).to_dict())
# does any such unit carry atmosphere?
fams=U[(U.c=="?")&U.car.isin(["HC","CH4"])].fam.unique()
names=[n for (n,) in db.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit'")]
for f in list(fams)[:12]:
  ex=[n for n in names if n.startswith(f)][:1]
  print(f, ex, "atm row:", any(n in atm for n in names if n.startswith(f)))
