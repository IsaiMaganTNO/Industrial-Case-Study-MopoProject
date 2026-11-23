import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
def elec(d,y):
    s=d["supply"]; e=s[(s.carrier=="electricity")&(s.year==y)]
    g=e.groupby("tech")["energy"].sum().sort_values(ascending=False)
    return g, g.sum()
for y in [2050]:
    go,to=elec(old,y); gn,tn=elec(new,y)
    print(f"=== P2 electricity supply {y} (GWh) ===")
    allt=sorted(set(go.index)|set(gn.index), key=lambda t:-max(go.get(t,0),gn.get(t,0)))
    print(f"{'tech':28s} {'baseline':>12s} {'share':>7s} {'gascap':>12s} {'share':>7s}")
    for t in allt[:14]:
        a=go.get(t,0.0); b=gn.get(t,0.0)
        if max(a,b)<500: continue
        print(f"{t:28s} {a:12,.0f} {a/to:6.1%} {b:12,.0f} {b/tn:6.1%}")
    print(f"{'TOTAL':28s} {to:12,.0f} {'':7s} {tn:12,.0f}")
