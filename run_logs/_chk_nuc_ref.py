import pickle,pandas as pd
RUN={"MR":"mr_ccslow_ccu_cap16_dac0","NATCAP":"ctryco2B_mr_ccslow_ccu_cap16_dac0","RP10":"rp10nb_mr_ccslow_ccu_cap16_dac0","CCSOPT":"mr_ccsopt_ccu_dac0"}
for k,v in RUN.items():
  F=pickle.load(open(rf"run_logs\{v}.pkl","rb"))
  f=F["fleet"]; f=f[f.tech.str.startswith("nuclear")&(f.year==2050)]
  print(k,"nuclear GW 2050 by country:",f.groupby(f.region.astype(str).str[:2]).units.sum().round(1).to_dict())
  s=F["supply"].query("year==2050"); g=s[s.tech.str.match(r"^(CCGT|OCGT)(?!-H2)")&(s.carrier=="electricity")]
  print("   gas power TWh by country:",(g.groupby(g.region.astype(str).str[:2]).energy.sum()/1e3).round(1).to_dict())
  r=s[s.tech.str.startswith("REF")]; print("   REF output by tech/country:",(r.groupby([r.tech,r.region.astype(str).str[:2]]).energy.sum()/1e3).round(1).to_dict())
