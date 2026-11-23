import sqlite3,json,collections,re
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
# units whose atmosphere ratio is keyed on a FUEL input (fuel-based) vs on own OUTPUT (route-based)
rs=m.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  JOIN parameter_value pv ON pv.entity_id=e.id
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE ec.name='unit_flow__unit_flow' AND pd.name='flow_ratio_equality_coefficient'
    AND e.name LIKE '%atmosphere%'""").fetchall()
fuelbased=collections.Counter(); routebased=collections.Counter()
for (n,) in rs:
    parts=n.split("__")
    unit=re.sub(r'_(NL|BE)C\d+$','',parts[0])
    key=parts[2] if len(parts)>2 else ""
    if key in ("coal","waste","crude","CH4","HC") or re.match(r'^(coal|waste|crude|CH4|HC|bio)',key):
        fuelbased[unit]+=1
    else: routebased[unit]+=1
print("FUEL-BASED emission booking (legacy defect), unit families:",len(fuelbased))
for k,v in fuelbased.most_common(14): print("   %-40s %d"%(k[:40],v))
print("\nROUTE-BASED families:",len(routebased))
m.close(); r.close()
