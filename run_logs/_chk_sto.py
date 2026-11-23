import pandas as pd,pickle,re
U=pd.read_pickle(r"run_logs\_use_elec_h2_all.pkl"); U=U[(U.year==2050)&(U.carrier=="elec")&U.tech.str.contains("storage|battery")]
U["typ"]=U.tech.str.replace(r"_[A-Z]{2}C?\d*__elec$","",regex=True)
print(U.groupby(["typ","run"]).twh.sum().unstack().round(1))
for k,v in {"MR":"mr_ccslow_ccu_cap16_dac0","RP10":"rp10nb_mr_ccslow_ccu_cap16_dac0"}.items():
  s=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["supply"].query("year==2050 and carrier=='electricity' and energy>0")
  s=s[s.tech.str.contains("storage|battery")]; print(k,(s.groupby(s.tech.str.replace(r"_[A-Z]{2}C?\d*$","",regex=True)).energy.sum()/1e3).round(1).to_dict())
  st=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["sto"].query("year==2050"); print("  GW/units", st.groupby("node").units.sum().round(1).to_dict())
