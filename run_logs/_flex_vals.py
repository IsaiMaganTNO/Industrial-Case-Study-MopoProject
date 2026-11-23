import sqlite3
c=sqlite3.connect(r"share_frlu_xpress_v4\input.sqlite")
q="""select e.name,pd.name,a.name,substr(cast(pv.value as text),1,200) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where e.name in ('bus-DR_BEC2') and pd.name='storage_investment_count_fix_cumulative'"""
for r in c.execute(q): print(r)
