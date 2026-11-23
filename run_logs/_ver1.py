import sqlite3,json,re,collections
A=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite"
B=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
CARBON={"coal","CH4","HC","crude","waste"}
def scan(db):
    c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
    fuel=collections.defaultdict(set); route=set()
    for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      JOIN parameter_value pv ON pv.entity_id=e.id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE ec.name='unit_flow__unit_flow' AND pd.name='flow_ratio_equality_coefficient'
        AND e.name LIKE '%__atmosphere__%'"""):
        p=n.split("__"); k=re.sub(r'_(NL|BE)C\d+$','',p[2])
        if k in CARBON: fuel[p[0]].add(k)
        else: route.add(p[0])
    c.close(); return fuel,route
fa,ra=scan(A); fb,rb=scan(B)
print("fuel-keyed units  : %d -> %d"%(len(fa),len(fb)))
print("route-keyed units : %d -> %d"%(len(ra),len(rb)))
both=[u for u in fb if u in rb]
print("DOUBLE-BOOKED (fuel AND route): %d  <-- must be 0"%len(both))
if both: print("   ",both[:5])
# aluminium check
c=sqlite3.connect("file:%s?mode=ro"%B,uri=True)
for n,v in c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='flow_ratio_equality_coefficient'
    AND e.name LIKE 'aluminium-primary-production-reference_NLC1%'"""):
    print("  AL:",n[:70],"=",v[:70])
c.close()
