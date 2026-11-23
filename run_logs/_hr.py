import sqlite3,json,collections
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
def prof(like):
    rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='unit_flow' AND e.name LIKE ? AND e.name LIKE '%elec%'""",(like,)).fetchall()
    h=collections.defaultdict(float)
    for n,v in rs:
        try:
            d=json.loads(v); d=d.get("data",d)
            items=d if isinstance(d,list) else list(d.items())
            for k,x in items:
                if k.startswith("2050-02-18"): h[k[11:16]]+=float(x)
        except Exception: pass
    return h
o=prof("%oil-eng%"); g=prof("%OCGT%"); b=prof("%battery-storage%")
cc=prof("%CCGT+CC%")
hrs=sorted(set(list(o)+list(g)+list(b)+list(cc)))
print("2050-02-18 hourly (MW)")
print("%-7s %9s %9s %9s %9s"%("hour","oil-eng","OCGT","battery","CCGT+CC"))
for hh in hrs:
    print("%-7s %9.2f %9.2f %9.2f %9.2f"%(hh,o.get(hh,0),g.get(hh,0),b.get(hh,0),cc.get(hh,0)))
c.close()
