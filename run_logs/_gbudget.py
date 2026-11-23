import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=\"fossil-CH4\" and pd.name=\"storage_state_max\" and al.name=\"limited_fossil-CH4\"").fetchone()
d=json.loads(bytes(r[0]).decode())["data"]
print("limited_fossil-CH4 storage_state_max (GWh budget):")
for k,v in d.items(): print(f"   {k[:4]}  {float(v):12.1f} GWh = {float(v)/1000:7.1f} TWh")
print()
print("vs unconstrained model usage: 2030 434.1 / 2040 624.4 / 2050 662.1 TWh")
