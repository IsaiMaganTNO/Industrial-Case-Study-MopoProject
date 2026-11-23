s=open("tools/make_deck_final3.py",encoding="utf8").read()
s=s.replace('''        for reg, v in (st0.groupby("region").co2.sum() / 1e3).items():
            pass
''','')
open("tools/make_deck_final3.py","w",encoding="utf8").write(s)
import pickle
for v in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","mr_ccslow_ccu_cap16_dac0"]:
    D=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")); c=D["co2net"].query("year==2050 and role=='captured'")
    c=c.assign(cn=c.region.astype(str).str[:2])
    print(v); print(c.pivot_table(index=["source"],columns="cn",values="co2",aggfunc="sum").div(1e3).round(2).to_string())
    print(c.groupby(["source","tech"]).co2.sum().div(1e3).round(2).to_string())
