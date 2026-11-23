import pickle
d=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
print(d["co2net"].query("role=='captured'").groupby("source").co2.sum().index.tolist())
print(d["inv"].category.unique().tolist())
print(sorted(d["inv"].query("category=='e-fuels / green chemicals' or category=='bioenergy' or category=='electrolysis'").tech.unique()))
s=d["supply"]; print(s[s.region.isna()].tech.unique()[:10], s.region.unique()[:5])
