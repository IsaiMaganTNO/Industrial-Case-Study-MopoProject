import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
rs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='connection' AND e.name LIKE '%CO2%'""").fetchall()
tonlc1=[n for (n,) in rs if n.endswith("NLC1")]
print("connections into NLC1:",tonlc1)
print("connections into NLC5:",[n for (n,) in rs if n.endswith("NLC5")])
print("connections into NLC6:",[n for (n,) in rs if n.endswith("NLC6")])
# capacity on a sample
for cn in rs[:1]+[(x,) for x in tonlc1[:2]]:
    p=m.execute("""SELECT pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE e.name=?""",(cn[0],)).fetchall()
    print(cn[0],"->",[(a,b[:22]) for a,b in p][:6])
m.close()
