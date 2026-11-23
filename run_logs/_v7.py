import pandas as pd, sqlite3
base=r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"
lo=r"verification\CO2_network(direct_link_ines_builder)\CO2_data_IC1_low_cost.xlsx"
hi=r"verification\CO2_network(direct_link_ines_builder)\CO2_data_IC1_high_cost.xlsx"
b=pd.read_excel(base,"network"); l=pd.read_excel(lo,"network"); h=pd.read_excel(hi,"network")
print("current == low_cost network tariffs:", b.tariff.round(9).equals(l.tariff.round(9)))
print("high/low tariff ratio: mean", round((h.tariff/l.tariff).mean(),4),
      " min",round((h.tariff/l.tariff).min(),4)," max",round((h.tariff/l.tariff).max(),4))
# which storage column is in the model? compare connection_flow_cost
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
vals=[]
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id
  where pd.name='connection_flow_cost' limit 2000"""):
    try: vals.append(float(bytes(v).decode()))
    except Exception: pass
print(f"\nmodel connection_flow_cost: n={len(vals)} min={min(vals):.5f} max={max(vals):.5f} mean={sum(vals)/len(vals):.5f}")
print("  low  network mean tariff/1000 =", round(l.tariff.mean()/1000,5))
print("  high network mean tariff/1000 =", round(h.tariff.mean()/1000,5))
