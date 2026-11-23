import pickle, sqlite3, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",200)
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0"]:
    X=pickle.load(open(rf"run_logs\{n}_xbbio.pkl","rb"))
    x=X["xb"].query("year==2050"); print("==",n); print((x.groupby(["car","o","d"]).v.sum()/1e3).round(1).to_string())
    b=X["bio"].query("year==2050"); print((b.groupby("c").v.sum()/1e3).round(1).to_dict())
c=sqlite3.connect(r"runs\3day_nb_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite")
uid=c.execute("select id from entity_class where name='unit'").fetchone()[0]
names=sorted({n.rsplit("_",1)[0] for (n,) in c.execute("select name from entity where class_id=?",(uid,))})
print([n for n in names if any(s in n.lower() for s in ["furn","e-","elec","(el)","heat","kiln","boiler","resist"])])
