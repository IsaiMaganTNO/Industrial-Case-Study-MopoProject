import pickle, pandas as pd, sqlite3
pd.set_option("display.width",250)
df=pickle.load(open(r"run_logs\mixedres_connflow.pkl","rb"))
ext={"FR","LU","CZ","AT","CH","PL","SE","FI","IE"}
x=df[df.c.isin(ext)]
inn=x[x.dir=="to_node"].groupby(["node","year"]).val.sum(); out=x[x.dir=="from_node"].groupby(["node","year"]).val.sum()
b=pd.concat([inn.rename("in"),out.rename("out")],axis=1).fillna(0); b["net_in"]=b["in"]-b["out"]
print("=== external-node connection balance (TWh)"); print((b/1e3).round(2).to_string())
c=sqlite3.connect(r"file:checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite?mode=ro",uri=True)
nodes=sorted(set(x.node))
print("\n=== model parameters on external nodes")
for n in nodes:
    ps=c.execute("""select pd.name, a.name, substr(cast(v.value as text),1,60) from parameter_value v join entity e on e.id=v.entity_id
      join parameter_definition pd on pd.id=v.parameter_definition_id join alternative a on a.id=v.alternative_id where e.name=?""",(n,)).fetchall()
    print(n, ps)
    u=c.execute("""select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name in ('unit__to_node','unit__from_node') and e.name like ?""",(f"%__{n}",)).fetchall()
    if u: print("   units:", [r[0] for r in u][:6])
