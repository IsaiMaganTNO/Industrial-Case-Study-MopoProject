import pickle
B=pickle.load(open(r"run_logs\nn_fix.pkl","rb"))
for k in ["supply","prod","emis"]:
  d=B[k];print(k,len(d),len(d.drop_duplicates()))
s=B["supply"];x=s[(s.tech=="CCGT-H2")&(s.region=="BEC6")&(s.carrier=="electricity")];print(x.to_string()[:800])
