import sqlite3,re,collections
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
u="aluminium-primary-production-reference_NLC1"
print("== all flow ratios for",u)
rs=m.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ?""",(u+"%",)).fetchall()
for n,v in rs: print("   %-80s %s"%(n[:80],v[:12]))
print("\n== aluminium unit families in DB")
rs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit' AND e.name LIKE '%alumin%'""").fetchall()
print(sorted(set(re.sub(r'_(NL|BE)C\d+$','',n) for (n,) in rs)))
m.close()
