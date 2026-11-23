import pickle, sqlite3
d=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
p=d["prod"]; print(p[p.tech.str.contains("SMR")].groupby(["tech","sector","year"]).output.sum())
s=d["supply"]; print(s[s.tech.str.contains("SMR")].groupby(["tech","carrier","year"]).energy.sum())
c=sqlite3.connect(r"runs\3day_nb_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite")
cl={n:i for i,n in c.execute("select id,name from entity_class")}
for cls in ["unit__to_node","unit__from_node"]:
    print(cls,[n for (n,) in c.execute("select name from entity where class_id=? and (name like 'REF-SMR-MEA_NLC2%' or name like 'SMR+CC_NLC2%')",(cl[cls],))])
