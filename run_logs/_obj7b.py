import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))["obj"]
b=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))["obj"]
ks=sorted(set(list(a.index)+list(b.index)))
print("%-30s %12s %12s"%("component","3day","7day"))
for k in ks:
    x=float(a.get(k,0)); y=float(b.get(k,0))
    print("%-30s %12.1f %12.1f"%(k[:30],x,y))
print("%-30s %12.1f %12.1f"%("TOTAL",sum(float(v) for v in a),sum(float(v) for v in b)))
