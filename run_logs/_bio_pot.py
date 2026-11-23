import sqlite3, glob
for f in ["1_IC1_NLBE_17zones", "3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK"]:
    db = glob.glob(rf"final_runs_pessimistic_ccs\{f}\input\*.sqlite")[0]; c = sqlite3.connect(db)
    print("==", f)
    for r in c.execute("select s.name, a.name, sa.rank from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id order by s.name, sa.rank"): print("  ", r)
    tot = {}
    for alt, name, val in c.execute("""select a.name, e.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
      join alternative a on a.id=pv.alternative_id where pd.name='storage_investment_count_max_cumulative' and e.name like 'biomass-stock_%' and e.name not like '%\\_\\_%' escape '\\'"""):
        cn = name.split("_")[1][:2]; tot[(alt, cn)] = tot.get((alt, cn), 0) + float(val)
    print("   potential by alternative/country:", {k: round(v, 1) for k, v in sorted(tot.items())})
    for r in c.execute("""select e.name, pd.name, substr(pv.value,1,80), a.name from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
      join alternative a on a.id=pv.alternative_id where e.name like 'biomass-stock_NLC3' and pd.name like '%cap%'"""): print("  ", r)
