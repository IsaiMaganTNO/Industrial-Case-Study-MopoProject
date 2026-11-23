import pickle
D=pickle.load(open(r"run_logs\_bal_sa_cl.pkl","rb"))
for k,d in D.items():
  x=d[(d.year==2050)&d.obj.str.match(r"^\((EL|H2)\)PEA_")&(d.dir=="from_node")&d.car.isin(["elec","H2"])]
  print(k,(x.assign(c=x.obj.str.extract(r"_(BE|NL)C\d+$")[0]).groupby(["c","car"]).v.sum()/1e3).round(1).to_dict())
