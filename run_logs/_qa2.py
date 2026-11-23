import pandas as pd, sqlite3, glob
b=pd.read_csv("results_2050_analysis/data/B5_industry_routes.csv")
b=b[b.run.isin(["MR","FRLU","CCSOPT"])&(b.share_pct>1)]
print(b.pivot_table(index=["sector","route_type"],columns="run",values="share_pct").round(0).fillna(0).to_string())
db=r"runs\rp10_mr_noblend\Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite"
c=sqlite3.connect(db)
q="""select e.name, pd.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
where e.name like '%iron-air%' and (pd.name like '%ratio%' or pd.name like '%loss%' or pd.name like '%eff%') limit 12"""
for r in c.execute(q): print(r[0],r[1],r[2][:60] if isinstance(r[2],bytes) else r[2])
