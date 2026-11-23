import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
def g(ent,p):
    r=c.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE e.name=? AND pd.name=?""",(ent,p)).fetchone()
    if not r: return None
    try:
        d=json.loads(r[0]); d=d.get("data",d)
        it=d if isinstance(d,list) else list(d.items())
        return {k[:4]:float(x) for k,x in it}
    except Exception: return float(r[0])
print("%-16s %10s %10s %8s %8s %8s"%("route","capex2050","fom","atm","CO2cap","elec"))
for fam in ["CEM2-(Afm)","CEM2-(Afm)MEA","LC3-(Afm)MEA"]:
    u=fam+"_BEC6"
    cap=g(u,"unit_investment_cost"); fom=g(u,"fom_cost")
    atm=g(u+"__atmosphere__"+u+"__cement_BEC6","flow_ratio_equality_coefficient")
    co2=g(u+"__CO2_BEC6__"+u+"__cement_BEC6","flow_ratio_equality_coefficient")
    el=g(u+"__cement_BEC6__elec_BEC6__"+u,"flow_ratio_equality_coefficient")
    print("%-16s %10.1f %10.4f %8s %8s %8s"%(fam[:16],cap["2050"],fom,atm,co2,el))
c.close()
