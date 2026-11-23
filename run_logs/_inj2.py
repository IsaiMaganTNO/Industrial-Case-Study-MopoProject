import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
def show(ent):
    rs=c.execute("""SELECT pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE e.name=?""",(ent,)).fetchall()
    print("==",ent)
    for p,v in rs: print("    %-36s %s"%(p[:36],v[:50]))
show("CO2-injection-NSNL031_NLC1")
show("CO2-storage-NSNL031")
c.close()
