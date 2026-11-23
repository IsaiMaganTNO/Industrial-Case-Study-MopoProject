import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
# how many injection units draw from atmosphere, and do they cost anything?
n=c.execute("""SELECT count(DISTINCT e.name) FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit' AND e.name LIKE 'atmosphere__CO2-injection%'""").fetchone()[0]
print("atmosphere -> CO2-injection links:",n)
u=c.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit' AND e.name LIKE 'CO2-injection%'""").fetchall()
print("injection units:",len(u))
withcost=0
for (name,) in u:
    r=c.execute("""SELECT count(*) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE e.name=? AND
      (pd.name LIKE '%cost%' OR pd.name LIKE '%investment%')""",(name,)).fetchone()[0]
    if r: withcost+=1
print("injection units with any cost/investment param:",withcost)
cap=c.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name='CO2-storage-NSNL031' AND pd.name='storage_investment_count_fix_cumulative'""").fetchone()[0]
print("NSNL031 fix cumulative:",json.loads(cap)["data"])
c.close()
