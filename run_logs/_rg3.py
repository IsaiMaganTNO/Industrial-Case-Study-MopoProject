import sqlite3,pandas as pd
c=sqlite3.connect(r"file:.spinetoolbox/items/biomass_db/biomass_db.sqlite?mode=ro",uri=True)
q="""SELECT e.name,a.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id
 WHERE pd.name='annual_production'"""
tot={}
for en,alt,v in c.execute(q):
    reg=en.split("__")[-1]
    tot.setdefault(alt,{})[reg]=float(v)
for alt in tot:
    s=sum(tot[alt].values())
    be=sum(v for k,v in tot[alt].items() if k.startswith("BEC"))
    nl=sum(v for k,v in tot[alt].items() if k.startswith("NLC"))
    print("%-12s total=%.1f GWh  BE=%.1f  NL=%.1f  -> BE %.1f PJ  NL %.1f PJ"%(alt,s,be,nl,be/277777.77*1,nl/277777.77*1))
