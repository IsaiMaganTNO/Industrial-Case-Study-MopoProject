import pickle, pandas as pd
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
caps={"wind-off-FB-SP370-HH155_NSBE01":5.235,"wind-off-FO-SP370-HH155_NSBE01":5.235,
 "wind-off-FB-SP370-HH155_NSNL011":9.8048,"wind-off-FB-SP370-HH155_NSNL012":6.1267,
 "wind-off-FB-SP370-HH155_NSNL031":17.4689,"wind-off-FB-SP370-HH155_NSNL033":5.8237,
 "wind-off-FO-SP370-HH155_NSNL033":5.8237,"wind-off-FB-SP370-HH155_NSNL032":3.6596}
f=A["fleet"]; f=f[f.year==2050]
g=f.groupby("tech").units.sum()
print(f"{'site':36} {'built':>8} {'cap':>8} {'util':>7}")
for k,v in sorted(caps.items()):
    b=g.get(k,0.0); print(f"{k:36} {b:8.3f} {v:8.3f} {b/v:7.1%}")
# BE combined FB+FO share one seabed zone? check sum
be=g.get("wind-off-FB-SP370-HH155_NSBE01",0)+g.get("wind-off-FO-SP370-HH155_NSBE01",0)
print(f"\nBE NSBE01 FB+FO total {be:.3f} vs single-zone cap 5.235 -> {be/5.235:.2f}x")
