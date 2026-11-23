import sqlite3,json,re
def fam(db):
    c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
    rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='storages_invested_available'""").fetchall()
    out={}
    for n,v in rs:
        core=n.replace("default_report__","").replace("__realization","")
        f=re.sub(r'_(NL|BE)C\d+$','',core)
        try:
            d=json.loads(v); d=d.get("data",d)
            items=d if isinstance(d,list) else list(d.items())
            for k,x in items:
                y=k[:4]
                if y in ("2030","2040","2050"):
                    out.setdefault(f,{}).setdefault(y,0.0); out[f][y]+=float(x)
        except Exception: pass
    c.close(); return out
a=fam(r"checkpoints\Investment_Results.3day_hcco2.sqlite")
b=fam(r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite")
print("%-26s %-21s %-21s"%("family","3-day 30/40/50","7-day 30/40/50"))
for f in ["battery-storage","battery-storage-iron-air","car-DR","salt-cavern",
          "CO2-storage-NSNL012","biomass-stock"]:
    g=lambda d:"%7.2f %6.2f %6.2f"%(d.get(f,{}).get("2030",0),
        d.get(f,{}).get("2040",0),d.get(f,{}).get("2050",0))
    print("%-26s %-21s %-21s"%(f[:26],g(a),g(b)))
