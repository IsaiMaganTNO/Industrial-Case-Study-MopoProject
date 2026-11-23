import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
def el(d):
    s=d["supply"]; e=s[s.carrier=="electricity"]
    g=e.groupby(["tech","year"])["energy"].sum().unstack().fillna(0)
    # collapse offshore/battery variants
    def key(t):
        if t.startswith("wind-off-FB-SP"): return "wind-off-FB (new)"
        if t.startswith("wind-off-FO-SP"): return "wind-off-FO (new)"
        if t.startswith("wind-off-FB-existing"): return "wind-off-FB-existing"
        if t.startswith("battery-storage"): return "battery discharge"
        if t.startswith("PHS") or t.startswith("pumped"): return "pumped hydro"
        return t
    g.index=[key(t) for t in g.index]
    return g.groupby(level=0).sum()
a=el(old); b=el(new)
idx=sorted(set(a.index)|set(b.index))
a=a.reindex(idx).fillna(0); b=b.reindex(idx).fillna(0)
out=pd.DataFrame({ (y,run):(a if run=="base" else b)[y] for y in [2030,2040,2050] for run in ["base","gascap"]})
out=out[out.abs().sum(axis=1)>200].sort_values((2050,"gascap"),ascending=False)
pd.set_option("display.width",200)
print("=== ELECTRICITY SUPPLY (GWh) ===")
print(out.round(0).to_string())
print()
print("TOTALS:", {y:(round(a[y].sum()),round(b[y].sum())) for y in [2030,2040,2050]})
