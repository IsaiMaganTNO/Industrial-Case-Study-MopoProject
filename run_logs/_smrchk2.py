import pickle
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","nb_ccslow"]:
    d=pickle.load(open(rf"run_logs\{n}.pkl","rb"))
    f=d["fleet"]; print(n,"fleet SMR+CC",f[f.tech.str.startswith("SMR+CC")].groupby("year").units.sum().to_dict(),
      "inv",d["inv"][d["inv"].tech.str.startswith("SMR+CC")].units.sum())
    s=d["supply"]; print(" H2 supply techs 2050", (s.query("carrier=='hydrogen' and year==2050").groupby("tech").energy.sum()/1e3).round(1).to_dict())
    c=d["co2net"]; print(" REF-SMR-MEA capture", (c[c.tech=="REF-SMR-MEA"].query("role=='captured'").groupby("year").co2.sum()/1e3).round(1).to_dict())
