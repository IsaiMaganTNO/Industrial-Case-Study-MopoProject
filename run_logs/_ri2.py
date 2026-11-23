import sqlite3,collections
def summary(p,label,regs=("DE","DK","NO","UK")):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    print("=== %s"%label)
    cls=collections.Counter(r[0] for r in c.execute("SELECT ec.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id"))
    print("  classes:",dict(cls))
    pds=collections.Counter(r[0] for r in c.execute("""SELECT pd.name FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id"""))
    print("  params:",dict(pds))
    alts=[r[0] for r in c.execute("SELECT name FROM alternative")]
    print("  alternatives:",alts[:14])
    c.close()
for it,lab in [("heat_db","EU heat"),("transport_db","EU transport"),("industry_db","EU industry"),("Other_Industry_DB","EU other_industry")]:
    summary(r"EU_case\.spinetoolbox\items\%s\%s.sqlite"%(it.lower() if it!="Other_Industry_DB" else "other_industry_db",it),lab)
