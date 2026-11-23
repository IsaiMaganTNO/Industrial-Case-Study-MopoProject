import pickle
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
f=A["fleet"]; f=f[f.year==2050]; g=f.groupby("tech").units.sum()
area={"NSBE01":3490.060068,"NSNL011":13072.298108,"NSNL012":20874.523573,
      "NSNL031":12615.611310,"NSNL032":6343.347802,"NSNL033":4437.287798}
print(f"{'zone':9}{'FB':>8}{'FO':>8}{'exist':>8}{'TOTAL':>9}{'zonecap':>9}{'MW/km2':>9}")
caps={"NSBE01":5.235,"NSNL011":9.8048,"NSNL012":6.1267,"NSNL031":17.4689,"NSNL032":3.6596,"NSNL033":5.8237}
tot=0
for z in area:
    fb=g.get(f"wind-off-FB-SP370-HH155_{z}",0.0)
    fo=g.get(f"wind-off-FO-SP370-HH155_{z}",0.0)
    ex=g.get(f"wind-off-FB-existing_{z}",0.0)
    t=fb+fo+ex; tot+=t
    print(f"{z:9}{fb:8.2f}{fo:8.2f}{ex:8.2f}{t:9.2f}{caps[z]:9.2f}{t/area[z]*1000:9.2f}")
print(f"\nTOTAL offshore 2050: {tot:.2f} GW; sum of per-tech zone caps {sum(caps.values()):.2f} GW")
