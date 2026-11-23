import sqlite3, collections
p=r".spinetoolbox\items\ines_db\ines_db.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
T=("DE","DK","NO","UK")
q="""SELECT pd.name, e.name FROM parameter_value pv
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     JOIN entity e ON e.id=pv.entity_id"""
rows=c.execute(q).fetchall()
print("=== VRE profile coverage for new countries ===")
for par in ["profile_limit_upper","units_existing","capacity","flow_profile"]:
    hit=collections.Counter()
    for pn,en in rows:
        if pn==par:
            s=en.rsplit("_",1)[-1]
            if s in T: hit[s]+=1
    print("  %-22s %s"%(par,dict(sorted(hit.items())) or "NONE"))
print("\n=== sample wind/solar entities per country ===")
for cc in T:
    s=[en for pn,en in rows if pn=="profile_limit_upper" and en.rsplit("_",1)[-1]==cc]
    print("  %-3s %d profiles; e.g. %s"%(cc,len(s),s[:3]))
c.close()
