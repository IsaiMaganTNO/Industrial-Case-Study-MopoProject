import sqlite3,glob
for f in [r"1_IC1_NLBE_17zones",r"2_CountryLevel_NLBE"]:
    db=glob.glob(rf"final_runs_pessimistic_ccs\{f}\input\*.sqlite")[0]; c=sqlite3.connect(db); print("==",f)
    q="""select e.name,pd.name,substr(pv.value,1,80) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
    where e.name like '%heatpump-ratio%' and (e.name like '%NLC4%' or e.name like '%NL' or e.name like '%NL_%' or e.name like 'heatpump-ratio_NL%')"""
    for r in c.execute(q): print(r)
    print([r[0] for r in c.execute("select name from entity where name like 'heatpump-ratio%'")])
