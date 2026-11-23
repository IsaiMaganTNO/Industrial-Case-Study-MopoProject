import sqlite3
c=sqlite3.connect(r"checkpoints\Investment_Results.3day_retireall.sqlite").cursor()
c.execute("""select pd.name, cast(pv.value as text) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 where pd.name like 'objective_%' or pd.name='total_costs'""")
for n,v in sorted(c.fetchall()):
    try:
        import json; d=json.loads(v); val=sum(float(x) for x in d.get("data",{}).values())
    except Exception: val=float(v)
    print("%-40s %16.2f"%(n,val))
