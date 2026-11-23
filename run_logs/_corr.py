import pickle, sqlite3, pandas as pd
pd.set_option("display.width",108)
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
b=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite")
old={r[0] for r in b.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection'")}
a=A["co2pipe"]; a=a[a["year"].astype(str).str.startswith("2050")].groupby("connection")["co2"].sum()
bb=B["co2pipe"]; bb=bb[bb["year"].astype(str).str.startswith("2050")].groupby("connection")["co2"].sum()
df=pd.DataFrame({"baseline":a,"bidir":bb}).fillna(0.0)
df=df[(df.abs()>1e-6).any(axis=1)]
df["NEW"]=[("NEW" if i not in old else "") for i in df.index]
df=df.sort_values("bidir",ascending=False)
print("2050 CO2 pipeline flows (ktCO2):")
print(df.round(1).to_string())
