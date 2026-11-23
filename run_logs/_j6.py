import pickle
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
A=pickle.load(open("run_logs/retireall.pkl","rb"))
for lbl,d in (("retireall",A),("hcco2",B)):
    s=d["supply"]; f=d["fleet"]
    print(f"-- {lbl} 2050 --")
    for t in ("CCGT","CCGT+CC","OCGT","CCGT-H2","oil-eng"):
        e=s[(s.year==2050)&(s.tech==t)].energy.sum()
        u=f[(f.year==2050)&(f.tech==t)].units.sum()
        cf=e/(u*8760) if u else float("nan")
        print(f"   {t:9s} GWh {e:10.1f}  units {u:7.3f}  implied CF {cf:6.3f}")
