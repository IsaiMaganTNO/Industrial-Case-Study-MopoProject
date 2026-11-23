import pickle,pandas as pd,sqlite3,glob
pd.set_option("display.width",250)
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
for k,v in R.items():
    D=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")); s=D["supply"]; s=s[(s.year==2050)&(s.carrier=="heat")&(s.energy>0)]
    print(k); print(s.pivot_table(index="region",columns="tech",values="energy",aggfunc="sum").fillna(0).div(1e3).round(1).to_string())
db=glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]
c=sqlite3.connect(db)
q="""select e.name,pd.name,pv.type,substr(pv.value,1,120) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
where (e.name like 'ground-heatpump%' or e.name like 'air-heatpump%') and e.name not like '%cool%' and (e.name like '%NLC2%' or e.name like '%heatpump') """
for r in c.execute(q).fetchall()[:40]: print(r)
