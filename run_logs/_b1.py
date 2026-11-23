import sqlite3, pandas as pd, re
pd.set_option("display.width",95); pd.set_option("display.max_rows",300)
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
EXT=("UK","DE","FR","NO","DK","LU")
names=[r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection'")]
rows=[]
for n in names:
    m=re.match(r"^(.*?)_([A-Za-z0-9]+)_(.*)$",n)
    parts=n.split("_")
    f=[p for p in parts if p in EXT]
    if f:
        car="?"
        for k in ("elec","CH4","H2","HC","MeOH","bio","CO2"):
            if "_"+k+"_" in n: car=k
        rows.append((car,n))
df=pd.DataFrame(rows,columns=["carrier","conn"])
print("foreign connections by carrier:"); print(df.carrier.value_counts().to_string())
print("TOTAL foreign connections:", len(df))
print()
nn=[r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='node'")]
print("foreign nodes:", [x for x in nn if any(x.endswith("_"+e) for e in EXT)])
