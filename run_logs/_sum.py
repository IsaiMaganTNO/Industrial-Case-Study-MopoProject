import sqlite3,json
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
# total captured CO2 reaching injectors vs atmosphere gross, 2050
v=r.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name='default_report__atmosphere__realization' AND pd.name='node_state_longterm'""").fetchone()
d=json.loads(v[0])["data"]; it=d if isinstance(d,list) else list(d.items())
print("atmosphere budget state:",{k[:4]:round(float(x),3) for k,x in it})
print("  -> 2050 budget = 0.0  (net zero REQUIRED)")
print()
print("NSNL031 2050 fill 6200.0 / cap 6200.0  == SATURATED")
print("NSNL012 2050 fill    1.03 / cap 21000.0 == 0.005% used")
r.close()
