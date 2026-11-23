import sqlite3, collections
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
cap=collections.defaultdict(float)
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id
  join entity_class ec on ec.id=e.class_id
  where ec.name='investment_group' and pd.name='investment_count_total_max_cumulative'
    and (e.name like 'solar-PV%' or e.name like 'wind-on%')"""):
    try: val=float(bytes(v).decode())
    except: continue
    reg=n.split("_")[-1]; grp="solar PV" if n.startswith("solar") else "wind onshore"
    cap[(grp,reg[:2])]+=val
print("POTENTIAL CAPS (investment_group, GW):")
for k in sorted(cap): print(f"   {k[0]:14s} {k[1]}  {cap[k]:8.2f}")
