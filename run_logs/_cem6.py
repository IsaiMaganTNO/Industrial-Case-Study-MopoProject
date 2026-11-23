import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
for fam in ["CEM2-(Afm)MEA","CEM2-(Afm)","EU-mix-2018","LC3-(Afm)MEA","(NG)DRI-EAF-MEA"]:
    rs=c.execute("""SELECT e.name,pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit' AND e.name GLOB ?
        AND pd.name LIKE '%fix%'""",(fam+"_*",)).fetchall()
    print("%-18s fix rows=%d"%(fam[:18],len(rs)))
    for n,p,v in rs[:2]: print("      ",n[:28],p[:34],v[:50])
c.close()
