import sqlite3,json,collections,re
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
CO2={"coal":0.35,"CH4":0.20,"HC":0.24,"crude":0.26,"waste":0.30}
# for every unit, which carbon fuels does it consume, and which is booked?
units=collections.defaultdict(lambda:{"in":set(),"booked":set()})
for (n,) in m.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit'"""):
    node,unit=n.split("__",1)
    base=re.sub(r'_(NL|BE)C\d+$','',node)
    if base in CO2: units[unit]["in"].add(base)
for (n,) in m.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  JOIN parameter_value pv ON pv.entity_id=e.id
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE ec.name='unit_flow__unit_flow' AND pd.name='flow_ratio_equality_coefficient'
    AND e.name LIKE '%__atmosphere__%'"""):
    p=n.split("__"); unit=p[0]
    key=re.sub(r'_(NL|BE)C\d+$','',p[2])
    if key in CO2: units[unit]["booked"].add(key)
gap=collections.Counter(); gapunits=[]
for u,d in units.items():
    miss=d["in"]-d["booked"]
    if d["booked"] and miss:
        fam=re.sub(r'_(NL|BE)C\d+$','',u)
        gap[fam]+=1; gapunits.append((u,sorted(d["booked"]),sorted(miss)))
print("units booking SOME fuel but missing others:",len(gapunits))
for k,v in gap.most_common(20): print("   %-44s %d"%(k[:44],v))
m.close(); r.close()
