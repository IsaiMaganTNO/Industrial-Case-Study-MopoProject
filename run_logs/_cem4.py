import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
def val(v):
    try:
        d=json.loads(v); d=d.get("data",d)
        it=d if isinstance(d,list) else list(d.items())
        return {k[:4]:round(float(x),4) for k,x in it}
    except Exception:
        try: return round(float(v),4)
        except Exception: return v[:28]
for fam in ["CEM2-(Afm)","CEM2-(Afm)MEA","LC3-(Afm)MEA"]:
    print("==",fam)
    for p in ("unit_investment_cost","fom_cost","investment_count_max_cumulative"):
        rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id
          JOIN entity_class ec ON ec.id=e.class_id
          WHERE ec.name='unit' AND e.name GLOB ? AND pd.name=?""",(fam+"_*",p)).fetchall()
        for n,v in rs[:2]: print("   %-26s %-30s %s"%(p[:26],n[:30],val(v)))
c.close()
