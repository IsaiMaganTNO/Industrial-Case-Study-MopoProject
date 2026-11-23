import pickle
D=pickle.load(open(r"run_logs\_bal_sa_cl.pkl","rb"))
for k,d in D.items():
  x=d[(d.car=="HC")&(d.year==2050)&(d.kind=="unit")]
  g=x.assign(g=x.obj.str.replace(r"_(BE|NL)C\d+$","",regex=True)).groupby(["dir","g"]).v.sum()/1e3
  print(k); print(g[g>1].round(1).sort_values().tail(14).to_string())
