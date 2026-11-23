import pickle
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
p=d["prod"]; e=d["emis"]
# check captured CO2 per route via co2store/co2pipe
print("co2store cols:",list(d["co2store"].columns))
cs=d["co2store"]
q=cs[cs["year"]==2050]
print(q.groupby([c for c in q.columns if q[c].dtype==object][0]).sum(numeric_only=True).head(12).to_string()[:900])
