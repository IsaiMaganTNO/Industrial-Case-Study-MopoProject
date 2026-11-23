import pickle
A,B,ex=pickle.load(open(r"run_logs\_cmp_in.pkl","rb"))
print(sorted({k[1] for k in B.keys()-A.keys() if k[2]=="unit_investment_cost"})[:5])
print(sorted({k[1] for k in B.keys()-A.keys() if k[2]=="connection_flow_cost"})[:6])
