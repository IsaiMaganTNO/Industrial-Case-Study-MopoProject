import sqlite3, json, statistics as st, datetime as dt
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def par(name,pname):
    return [(bytes(v).decode(),a) for v,a in c.execute(
      "select pv.value,al.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id "
      "join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=? and pd.name=?",(name,pname))]
def show(n):
    print(n)
    for pn in ["unit_investment_cost","unit_investment_lifetime","unit_investment_tech_discount_rate","fom_cost","vom_cost"]:
        for v,a in par(n,pn):
            try:
                d=json.loads(v)
                if isinstance(d,dict) and "data" in d and isinstance(d["data"],dict):
                    v="  ".join(f"{k[:4]}={float(x):9.1f}" for k,x in d["data"].items())
            except Exception: pass
            print(f"   {pn:36s} [{a:12s}] {str(v)[:100]}")
    print()
for n in ["wind-off-FO-SP370-HH155_NSNL031","wind-off-FB-SP370-HH155_NSNL031",
          "wind-on-SP277-HH100_NLC3","solar-PV-no-tracking_NLC3","nuclear-3_NLC3","CCGT+CC_NLC3"]:
    show(n)
