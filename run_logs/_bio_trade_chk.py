import pickle
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl","rb"))
b = d["bio"]; print(type(b)); print(getattr(b, "columns", None)); print(b.head(10).to_string() if hasattr(b,"head") else b)
f = pickle.load(open(r"run_logs\_flows2050_MR.pkl","rb"))
c = f[(f.kind=="connection_flow") & f.node.isin(["bio","biomass-stock","MeOH","HC"])]
print(c.obj.str.extract(r"^([A-Z]{2})[^_]*_([A-Za-z-]+)_([A-Z]{2})")[0].value_counts().head(), len(c))
print(c.groupby(["node","dir"]).v.sum().round(1))
print(c.obj.unique()[:20])
