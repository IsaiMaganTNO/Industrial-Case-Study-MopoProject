import pickle,pandas as pd
pd.set_option("display.width",200)
RUN={"IC1":"nb_ccslow_ccu_cap16_dac0","MR":"mr_ccslow_ccu_cap16_dac0"}
for k,v in RUN.items():
    F=pickle.load(open(rf"run_logs\{v}.pkl","rb"))
    c=F["co2net"];c=c[c.year==2050]
    print(k,"co2net roles:",c.groupby("role").co2.sum().div(1e3).round(2).to_dict())
    print(" captured by region:",c[c.role=="captured"].groupby("region").co2.sum().div(1e3).round(2).to_dict())
    print(" used/injected by tech-prefix:",c[c.role=="used / injected"].groupby(c.tech.str[:14]).co2.sum().div(1e3).round(2).to_dict())
    p=F["co2pipe"];print(" pipe cols",list(p.columns)); p=p[p.year==2050]
    print(p.groupby(["origin","dest"]).co2.sum().div(1e3).round(2).to_string())
    s=F["co2store"];s=s[s.year==2050];print(" store:",s.groupby(["reservoir","region"]).co2.sum().div(1e3).round(2).to_dict())
