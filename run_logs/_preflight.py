import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
q=lambda s,p=():c.execute(s,p).fetchall()
# 1 CO2 cap
v=q("""SELECT cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id WHERE e.name='atmosphere'
  AND pd.name='storage_investment_count_max_cumulative'""")[0][0]
d=json.loads(v)["data"]
print("CO2 cap 2030 %.8f  x1000x365 = %.1f"%(d["2030-01-01T00:00:00"],
      d["2030-01-01T00:00:00"]*1000*365))
print("CO2 cap 2041 %.8f  x1000x365 = %.1f"%(d["2041-01-01T00:00:00"],
      d["2041-01-01T00:00:00"]*1000*365))
# 2 HC CO2 rows
n=q("""SELECT count(*) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name LIKE '%atmosphere%HC%' AND typeof(pv.value)='blob'""")[0][0]
print("HC-CO2 entity rows:",n)
# 3 rep blocks
n=q("""SELECT count(*) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE pd.name='representative_block_index'""")[0][0]
print("representative_block_index rows:",n)
# 4 biomass cap rows
n=q("""SELECT count(*) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='storage_investment_count_max_cumulative'
    AND e.name LIKE 'biomass-stock%'""")[0][0]
print("biomass cap rows:",n)
c.close()
