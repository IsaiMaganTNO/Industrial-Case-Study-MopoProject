import sys; sys.path.insert(0,"tools"); import plot_run_summary as S, pickle
t=set()
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","mr_ccslow_ccu_cap16_dac0"]:
    d=pickle.load(open(rf"run_logs\{n}_NLBE.pkl","rb")); t|=set(d["prod"].query("year==2050 and sector in ['steel (primary)','olefins','glass (container)','cement','ammonia']").tech)
for x in sorted(t): print(x,"->",S.route_label(x))
