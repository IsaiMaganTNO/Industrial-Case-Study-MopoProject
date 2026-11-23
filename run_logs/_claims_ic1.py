import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
D=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
print(D.keys())
s=D["supply"]; s=s[s.energy>0]
print("== elec 2050 by tech"); e=s[(s.carrier=="electricity")]
print(e.groupby(["year","category"]).energy.sum().div(1e3).round(1).unstack(0).to_string())
print(e[e.year==2050].groupby("tech").energy.sum().div(1e3).round(1).sort_values().tail(25).to_string())
print("== H2"); h=s[s.carrier=="hydrogen"]; print(h.groupby(["year","tech"]).energy.sum().div(1e3).round(1).unstack(0).to_string())
print("== carriers list", sorted(s.carrier.unique()))
for car in [c for c in s.carrier.unique() if c not in("electricity","hydrogen")]:
    q=s[(s.carrier==car)&(s.year==2050)]; print("==",car); print(q.groupby("tech").energy.sum().div(1e3).round(1).sort_values().tail(12).to_string())
p=D["prod"]
for sec in ["ammonia","steel (primary)","olefins","cement"]:
    q=p[p.sector==sec]; t=q.groupby(["year","tech"]).output.sum().unstack(0); print("==",sec); print((t/t.sum()*100).round(1).to_string())
