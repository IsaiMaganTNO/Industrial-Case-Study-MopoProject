import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT DISTINCT e.name FROM entity e
  JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit' AND (e.name LIKE 'CEM2-%' OR e.name LIKE 'LC3-%')""").fetchall()
fams=sorted(set(n.rsplit("_",1)[0] for (n,) in rs))
print("cement unit families available:")
for f in fams: print("   ",f)
# is CEM2-(Afm)MEA capacity-limited?
for fam in ["CEM2-(Afm)MEA","CEM2-(Afm)"]:
    r=c.execute("""SELECT pd.name,count(*) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name LIKE ? AND pd.name LIKE '%investment%'
      GROUP BY pd.name""",(fam+"\\_%",)).fetchall()
    print(fam,"->",r)
c.close()
