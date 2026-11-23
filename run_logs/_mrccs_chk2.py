import sqlite3,pandas as pd
lo=pd.read_excel(r"verification\CO2_data_IC1_low_cost.xlsx",sheet_name="network"); hi=pd.read_excel(r"verification\CO2_data_IC1_high_cost.xlsx",sheet_name="network")
m=lo.merge(hi,on=["from","to","mode"],suffixes=("_lo","_hi")); same=m[abs(m.tariff_lo-m.tariff_hi)<1e-9]
print("routes with identical tariff:",len(same),same["mode"].value_counts().to_dict())
d=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_ccslow.sqlite"); a=sqlite3.connect(r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
Q="select e.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where pd.name='connection_flow_cost' and e.name like '%\_CO2\_%' escape '\\'"
A=dict(a.execute(Q)); B=dict(d.execute(Q)); un=sorted(k.split("__")[0] for k in A if A[k]==B[k]); print("unchanged in model:",un)
