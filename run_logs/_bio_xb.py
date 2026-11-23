import pickle, re
f = pickle.load(open(r"run_logs\_flows2050_MR.pkl","rb"))
c = f[(f.kind=="connection_flow") & (f.node=="bio")].copy()
m = c.obj.str.extract(r"^([A-Z]{2})[A-Z0-9]*_bio_([A-Z]{2})[A-Z0-9]*$")
c["a"], c["b"] = m[0], m[1]; c = c.dropna(subset=["a"])
x = c[(c.a != c.b) & (c.dir=="from_node")]
print("cross-border bio rows:", len(x)); print(x.groupby(["a","b","cn"]).v.sum().round(1).to_string())
print("bio conn objects w/ foreign end:", sorted({o for o in c.obj if any(k in o for k in ("DE","DK","NO","UK","FR"))})[:20])
