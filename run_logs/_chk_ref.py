import pickle,collections
hc=pickle.load(open(r"run_logs\_hc_supply_all.pkl","rb"))
for k in ["MR","S1","S2","S3"]:
  d=collections.defaultdict(float)
  for (t,c,y),v in hc[k].items():
    if y==2050 and v>0: d[(t,c)]+=v
  print(k,{f"{t}|{c}":round(v) for (t,c),v in sorted(d.items())})
