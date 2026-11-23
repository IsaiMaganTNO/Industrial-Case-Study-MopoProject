import pandas as pd
R=pd.read_csv(r"final_runs_pessimistic_ccs\report_2050\4_h2_elec_balance_B_2050.csv")
Ra=pd.read_csv(r"final_runs_pessimistic_ccs\report_2050\4_h2_elec_balance_A_2050.csv"); R=pd.concat([Ra,R]).drop_duplicates()
print(R.pivot_table(index=["carrier","side","item"],columns="run",values="twh",aggfunc="sum").round(1).to_string())
import pickle
RUN={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0","MR":"mr_ccslow_ccu_cap16_dac0","NATCAP":"ctryco2B_mr_ccslow_ccu_cap16_dac0","RP10":"rp10nb_mr_ccslow_ccu_cap16_dac0","CCSOPT":"mr_ccsopt_ccu_dac0"}
for k,v in RUN.items():
  s=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["supply"].query("year==2050")
  e=s[(s.carrier=="electricity")&(s.energy>0)]; h=s[(s.carrier=="hydrogen")&(s.energy>0)]
  print(k,"elec supply",round(e.energy.sum()/1e3,1),"of which storage discharge",round(e[e.tech.str.contains("storage|battery")].energy.sum()/1e3,1),"| H2 supply",round(h.energy.sum()/1e3,1), "H2 storage disch", round(h[h.tech.str.contains("storage|tank|cavern")].energy.sum()/1e3,1))
