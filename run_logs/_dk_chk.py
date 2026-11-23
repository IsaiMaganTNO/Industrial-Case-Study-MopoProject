import pickle
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb"))
e = d["emis"].query("year==2050 and region=='DK'")
print("total", round(e.co2.sum()/1e3,2))
for (c, t), v in e.groupby(["category","tech"]).co2.sum().items():
    if abs(v) > 100: print(f"{v/1e3:8.2f} Mt  {c} | {t}")
